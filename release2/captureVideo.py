import time
import cv2
import numpy as np
import constants
import io
import playSound
import cameraSyncerMaster
import cameraSyncerSlave
import os

# ---------------------------------------------------------------------------
# Pi5 uses picamera2 (libcamera stack).  Pi4 used the legacy picamera library.
# We detect the platform and import the appropriate backend.
# ---------------------------------------------------------------------------

def _is_pi5():
    return os.uname()[1] == constants.Info.PI5_UNAME


if _is_pi5():
    from picamera2 import Picamera2
    from picamera2.encoders import MJPEGEncoder
    from picamera2.outputs import Output as _Picamera2Output
else:
    try:
        from picamera import PiCamera
    except ImportError:
        PiCamera = None  # allow import on non-Pi dev machines


# ---------------------------------------------------------------------------
# picamera2 compatibility wrapper
# ---------------------------------------------------------------------------

class PiCamera2Compat:
    """Wraps Picamera2 to expose the subset of the picamera.PiCamera API used
    by this firmware.  All timestamp values are in **microseconds** to match
    the existing code that was written for picamera.
    """

    # Picamera2 SensorTimestamp is in nanoseconds; divide by 1000 for µs.
    _NS_TO_US = 1000

    class _FrameProxy:
        """Mimics ``picamera.PiCamera.frame``."""
        def __init__(self):
            self.timestamp = None  # updated on every output frame

    class _TimestampedOutput(_Picamera2Output if _is_pi5() else object):
        """picamera2 Output subclass that forwards MJPEG frames to the
        RealTimeProcessing stream and keeps the camera wrapper's frame
        timestamp up-to-date."""
        def __init__(self, stream, wrapper):
            if _is_pi5():
                super().__init__()
            self._stream = stream
            self._wrapper = wrapper

        def outputframe(self, frame, keyframe=True, timestamp=None, packet=None):
            if timestamp is not None:
                # Convert nanoseconds → microseconds
                ts_us = timestamp // PiCamera2Compat._NS_TO_US
                self._wrapper.frame.timestamp = ts_us
                self._wrapper._last_ts_us = ts_us
            if frame:
                self._stream.write(frame)

    # ------------------------------------------------------------------

    def __init__(self, camera_num=0, resolution=(1920, 1080)):
        self._camera_num = camera_num
        self._resolution = resolution
        self._framerate = float(constants.Scanning.FRAME_RATE)
        self._shutter_speed = int(constants.Scanning.EXPOSURE_TIME_SCAN * 1000)
        self._iso = constants.Scanning.ISO
        self._awb_gains = (1.9, 1.2)
        self._zoom = (0, 0, 1, 1)
        self._recording = False
        self._encoder = None
        self._output_obj = None
        self._last_ts_us = None
        self.frame = PiCamera2Compat._FrameProxy()
        self.closed = True

        # Create and configure the Picamera2 instance
        self._cam = Picamera2(camera_num)
        self._configure()
        self._cam.start()
        self.closed = False

    def _configure(self):
        """Build and apply a video configuration."""
        frame_dur = int(1_000_000 / self._framerate)
        config = self._cam.create_video_configuration(
            main={'size': self._resolution, 'format': 'YUV420'},
            controls={
                'NoiseReductionMode': 0,              # image_denoise = False
                'FrameDurationLimits': (frame_dur, frame_dur),
                'AeEnable': False,
                'AwbEnable': False,
                'ExposureTime': self._shutter_speed,
                'ColourGains': self._awb_gains,
            }
        )
        self._cam.configure(config)

    # ---- properties that mirror picamera.PiCamera ----

    @property
    def framerate(self):
        return self._framerate

    @framerate.setter
    def framerate(self, fps):
        self._framerate = float(fps)
        frame_dur = int(1_000_000 / fps)
        try:
            self._cam.set_controls({'FrameDurationLimits': (frame_dur, frame_dur)})
        except Exception as e:
            print('PiCamera2Compat framerate set error:', e)

    @property
    def framerate_delta(self):
        return 0.0

    @framerate_delta.setter
    def framerate_delta(self, delta):
        """Fine-tune the frame rate for inter-camera synchronisation."""
        effective_fps = self._framerate + delta
        if effective_fps > 0:
            frame_dur = int(1_000_000 / effective_fps)
            try:
                # Allow some flexibility so the camera can self-adjust
                self._cam.set_controls({'FrameDurationLimits': (1, frame_dur)})
            except Exception as e:
                print('PiCamera2Compat framerate_delta set error:', e)

    @property
    def shutter_speed(self):
        return self._shutter_speed

    @shutter_speed.setter
    def shutter_speed(self, usec):
        self._shutter_speed = int(usec)
        try:
            self._cam.set_controls({'ExposureTime': int(usec), 'AeEnable': False})
        except Exception as e:
            print('PiCamera2Compat shutter_speed set error:', e)

    @property
    def exposure_speed(self):
        """Approximate read-back of actual exposure (µs)."""
        try:
            return self._cam.capture_metadata().get('ExposureTime', self._shutter_speed)
        except Exception:
            return self._shutter_speed

    @property
    def iso(self):
        return self._iso

    @iso.setter
    def iso(self, value):
        self._iso = value
        if value > 0:
            gain = value / 100.0
            try:
                self._cam.set_controls({'AnalogueGain': gain})
            except Exception as e:
                print('PiCamera2Compat iso set error:', e)

    @property
    def analog_gain(self):
        try:
            return self._cam.capture_metadata().get('AnalogueGain', self._iso / 100.0)
        except Exception:
            return self._iso / 100.0

    @property
    def digital_gain(self):
        try:
            return self._cam.capture_metadata().get('DigitalGain', 1.0)
        except Exception:
            return 1.0

    @property
    def exposure_mode(self):
        return 'off'

    @exposure_mode.setter
    def exposure_mode(self, mode):
        ae = (mode not in ('off', 'fixedfps'))
        try:
            self._cam.set_controls({'AeEnable': ae})
        except Exception as e:
            print('PiCamera2Compat exposure_mode set error:', e)

    @property
    def awb_mode(self):
        return 'off'

    @awb_mode.setter
    def awb_mode(self, mode):
        enabled = (mode != 'off')
        try:
            self._cam.set_controls({'AwbEnable': enabled})
        except Exception as e:
            print('PiCamera2Compat awb_mode set error:', e)

    @property
    def awb_gains(self):
        return self._awb_gains

    @awb_gains.setter
    def awb_gains(self, gains):
        self._awb_gains = (float(gains[0]), float(gains[1]))
        try:
            self._cam.set_controls({'ColourGains': self._awb_gains})
        except Exception as e:
            print('PiCamera2Compat awb_gains set error:', e)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, zoom_tuple):
        self._zoom = zoom_tuple
        x, y, w, h = zoom_tuple
        full_w, full_h = self._resolution
        crop = (int(x * full_w), int(y * full_h), int(w * full_w), int(h * full_h))
        try:
            self._cam.set_controls({'ScalerCrop': crop})
        except Exception as e:
            print('PiCamera2Compat zoom set error:', e)

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, res):
        self._resolution = res
        # Resolution change requires reconfiguration; done via updateCameraSettings

    @property
    def sensor_mode(self):
        return 1  # picamera2 selects mode automatically

    @sensor_mode.setter
    def sensor_mode(self, mode):
        pass  # managed automatically by picamera2

    @property
    def clock_mode(self):
        return 'raw'

    @clock_mode.setter
    def clock_mode(self, mode):
        pass  # picamera2 always provides absolute sensor timestamps

    @property
    def image_denoise(self):
        return False

    @image_denoise.setter
    def image_denoise(self, value):
        mode = 0 if not value else 1
        try:
            self._cam.set_controls({'NoiseReductionMode': mode})
        except Exception as e:
            print('PiCamera2Compat image_denoise set error:', e)

    @property
    def timestamp(self):
        """Current camera hardware timestamp in microseconds.
        Returns the timestamp of the most recently received frame, or polls
        capture_metadata() if no frame has arrived yet.
        """
        if self._last_ts_us is not None:
            return self._last_ts_us
        try:
            meta = self._cam.capture_metadata()
            return meta.get('SensorTimestamp', 0) // self._NS_TO_US
        except Exception:
            return 0

    @property
    def recording(self):
        return self._recording

    # ---- camera control methods ----

    def start_preview(self):
        pass  # no-op; Pi5 is headless

    def stop_preview(self):
        pass

    def close(self):
        try:
            if self._recording:
                self.stop_recording()
            self._cam.stop()
            self._cam.close()
        except Exception as e:
            print('PiCamera2Compat close error:', e)
        finally:
            self.closed = True

    def start_recording(self, stream, format='mjpeg', bitrate=None, resize=None):
        """Start MJPEG recording; each frame is forwarded to *stream*.write()."""
        if self._recording:
            self.stop_recording()
        self._encoder = MJPEGEncoder(bitrate or constants.Scanning.BIT_RATE)
        self._output_obj = PiCamera2Compat._TimestampedOutput(stream, self)
        try:
            self._cam.start_recording(self._encoder, self._output_obj)
            self._recording = True
            print('start_recording (picamera2)')
        except Exception as e:
            print('PiCamera2Compat start_recording error:', e)

    def stop_recording(self):
        try:
            self._cam.stop_recording()
            print('stop_recording (picamera2)')
        except Exception as e:
            print('PiCamera2Compat stop_recording error:', e)
        finally:
            self._recording = False

    def wait_recording(self, seconds):
        time.sleep(seconds)

    def capture(self, output, format='yuv', use_video_port=False, resize=None):
        """Single-frame capture; mimics picamera.PiCamera.capture()."""
        try:
            if format == 'yuv':
                arr = self._cam.capture_array('main')  # returns YUV420
                if isinstance(output, np.ndarray):
                    np.copyto(output[:arr.size], arr.flatten()[:output.size])
                else:
                    output.write(arr.tobytes())
            elif format in ('jpeg', 'jpg'):
                buf = io.BytesIO()
                self._cam.capture_file(buf, format='jpeg')
                buf.seek(0)
                if hasattr(output, 'write'):
                    output.write(buf.read())
                else:
                    output.seek(0)
                    output.write(buf.read())
            elif format in ('bgr', 'rgb'):
                arr = self._cam.capture_array('main')
                if isinstance(output, np.ndarray):
                    np.copyto(output[:arr.size], arr.flatten()[:output.size])
        except Exception as e:
            print('PiCamera2Compat capture error:', e)

    def capture_sequence(self, outputs, format='yuv', use_video_port=False, resize=None):
        """Capture a sequence of frames."""
        for out in outputs:
            self.capture(out, format=format, use_video_port=use_video_port, resize=resize)


# ---------------------------------------------------------------------------
# Main capture class (Pi4 and Pi5)
# ---------------------------------------------------------------------------

class capture():
    camera = None

    def __init__(self, preview=False, camera_id=0):
        """
        :param camera_id: 0 = left/master camera (CSI-0),
                          1 = right/slave camera (CSI-1, Pi5 only).
        """
        self.camera_id = camera_id
        self.currentBitRate = 0
        self.openCamera(preview)

        # SET UP SYNCING
        self.mSyncerMaster = cameraSyncerMaster.cameraSyncerMaster(self.camera)
        self.mSyncerSlave = cameraSyncerSlave.cameraSyncerSlave(self.camera)

    def openCamera(self, preview=False):
        if self.isOpen():
            print('Camera already open')
            return

        if _is_pi5():
            # Pi5: use picamera2 wrapper
            self.camera = PiCamera2Compat(
                camera_num=self.camera_id,
                resolution=constants.Scanning.RESOLUTION
            )
        else:
            # Pi4: use legacy picamera
            self.camera = PiCamera(
                resolution=constants.Scanning.RESOLUTION,
                sensor_mode=constants.Scanning.CAMERA_MODE
            )

        self.camera.iso = constants.Scanning.ISO
        self.setExposure(constants.Scanning.EXPOSURE_TIME_SCAN)
        self.camera.exposure_mode = 'off'
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = (1.9, 1.2)
        self.camera.clock_mode = 'raw'
        self.camera.image_denoise = False

        self.updateCameraSettings()

        if preview and not _is_pi5():
            self.camera.start_preview()
            print('start preview')

    def closeCamera(self):
        try:
            self.camera.stop_preview()
        except Exception as e:
            print("Warning: camera close preview error", e)
        try:
            self.camera.close()
            print("camera closed")
        except Exception as e:
            print("Warning: camera close error", e)

    def isOpen(self):
        try:
            closed = self.camera.closed
        except Exception:
            return False
        return not closed

    def printSettings(self):
        print('SENSOR_MODE : ', self.camera.sensor_mode)
        print('EXPOSURE    : ', self.camera.shutter_speed, self.camera.exposure_speed)
        print('ISO         : ', self.camera.iso)
        print('ANALOG GAIN : ', self.camera.analog_gain)
        print('DIGITAL GAIN: ', self.camera.digital_gain)
        print('AWB         : ', self.camera.awb_mode, self.camera.awb_gains)
        print('FRAME RATE  : ', float(self.camera.framerate))
        print('RESOLUTION  : ', self.camera.resolution)
        print('RESIZE      : ', constants.Scanning.RESIZE)

    def updateCameraSettings(self):
        if not self.isOpen():
            print('camera closed - settings not changed')
            return

        restartRecording = False

        if self.currentBitRate != constants.Scanning.BIT_RATE:
            restartRecording = True

        if not _is_pi5():
            # sensor_mode / resolution / framerate changes require stop+start on Pi4
            if self.camera.sensor_mode != constants.Scanning.CAMERA_MODE:
                if self.camera.recording:
                    self.camera.stop_recording()
                    restartRecording = True
                self.camera.sensor_mode = constants.Scanning.CAMERA_MODE
                self.camera.sensor_mode = constants.Scanning.CAMERA_MODE  # docs say set it twice

            if self.camera.resolution != constants.Scanning.RESOLUTION:
                if self.camera.recording:
                    self.camera.stop_recording()
                    restartRecording = True
                self.setResolution(constants.Scanning.RESOLUTION)

            if self.camera.framerate != constants.Scanning.FRAME_RATE:
                if self.camera.recording:
                    self.camera.stop_recording()
                    restartRecording = True
                self.setFrameRate(constants.Scanning.FRAME_RATE)

        if restartRecording:
            self.startVideoAndProcessing()

        # SETUP CAMERA ALIGNMENT
        # On Pi5 use camera_id to determine left/right; on Pi4 use hostname.
        if _is_pi5():
            zoom = constants.Scanning.ZOOM_L if self.camera_id == 0 else constants.Scanning.ZOOM_R
        elif os.uname()[1] == constants.Info.MASTER_UNAME:
            zoom = constants.Scanning.ZOOM_L
        else:
            zoom = constants.Scanning.ZOOM_R

        self.camera.zoom = zoom

        # SET EXPOSURE
        if not _is_pi5():
            # picamera-specific ISO/exposure logic
            if self.camera.iso != constants.Scanning.ISO:
                if constants.Scanning.ISO < 100:
                    self.camera.iso = constants.Scanning.ISO
                    time.sleep(0.25)
                    self.camera.exposure_mode = 'off'
                else:
                    self.camera.exposure_mode = 'fixedfps'
                    time.sleep(0.25)
                    self.camera.iso = constants.Scanning.ISO

        if self.camera.shutter_speed != constants.Scanning.EXPOSURE_TIME_SCAN:
            self.setExposure(constants.Scanning.EXPOSURE_TIME_SCAN)

        if constants.Scanning.RESIZE is None:
            self.CAMERA_RES = self.camera.resolution
        else:
            self.CAMERA_RES = constants.Scanning.RESIZE

        self.printSettings()

    def setResolution(self, resolution):
        self.camera.resolution = resolution

    def setFrameRate(self, frameRate):
        self.camera.framerate = frameRate
        # Update the RealTimeProcessing frame time for whichever instance owns this camera
        rt = self._get_realtime()
        if rt is not None:
            rt.updateFrameTime(frameRate)

    def _get_realtime(self):
        """Return the RealTimeProcessing instance that belongs to this camera."""
        if _is_pi5() and self.camera_id == 1:
            return constants.Control.mRealTimeRight
        return constants.Control.mRealTime

    def setExposure(self, msec):
        print('exp request', int(msec * 1000))
        self.camera.shutter_speed = int(msec * 1000)

    def setExposureAndMaxFrameRate(self, msec):
        frameRate = 1000 / msec
        if frameRate > constants.Scanning.MAX_FRAME_RATE:
            frameRate = constants.Scanning.MAX_FRAME_RATE
        self.setFrameRate(frameRate)
        self.camera.shutter_speed = int(msec * 1000)
        self.printSettings()

    def roundExposure(self, msec):
        msec = round(msec / 10) * 10
        return msec

    def setAutoExposureThenLock(self):
        bestExposure = constants.Scanning.AUTO_EXPOSURE_LIST[0]
        bestMax = -1
        borderTrimL = 100
        borderTrimR = 300
        borderTrimT = 100
        borderTrimB = 0
        if self.camera.recording:
            self.camera.stop_recording()
        for msec in constants.Scanning.AUTO_EXPOSURE_LIST:
            self.setExposureAndMaxFrameRate(msec)
            mStream = self.captureColourJPG()  # first image is discarded
            mStream = self.captureColourJPG()
            mStream.seek(0, 0)
            string = mStream.read()
            array = np.frombuffer(string, np.uint8)
            mStream.close()
            testImage = cv2.imdecode(array, cv2.IMREAD_COLOR)
            testImage = testImage[borderTrimT:testImage.shape[0] - borderTrimB,
                                  borderTrimL:testImage.shape[1] - borderTrimR]
            scale = constants.Scanning.AUTO_EXPOSURE_DOWNSCALE / testImage.shape[0]
            testImage = cv2.resize(testImage, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            maxGrey = np.max(testImage)
            print('msec, max grey:', msec, maxGrey)
            if maxGrey > constants.Scanning.AUTO_EXPOSURE_TARGET_MAX:
                print('Rejected', msec, 'could cause saturation: >', constants.Scanning.AUTO_EXPOSURE_TARGET_MAX,
                      'maxGrey was', maxGrey)
                break
            else:
                bestExposure = msec
                bestMax = maxGrey

        print('Auto Exposure chosen as:', bestExposure, ' targetMax:', constants.Scanning.AUTO_EXPOSURE_TARGET_MAX,
              ' with max grey:', bestMax)
        self.setFrameRate(constants.Scanning.MAX_FRAME_RATE)
        self.setExposureAndMaxFrameRate(bestExposure)
        if bestExposure < 12:
            print('HIGH AMBIENT LIGHT OR STONG REFLECTION WARNING')
            playSound.file(soundCode=constants.Sounds.HIGH_AMBIENT_LIGHT)
        return bestExposure

    def getOpticalAngleImage(self):
        if _is_pi5():
            try:
                arr = self.camera._cam.capture_array('main')
                h, w = arr.shape[:2]
                # Return Y channel only
                return arr[:h, :w].copy() if arr.ndim == 2 else arr[:h, :w, 0].copy()
            except Exception as e:
                print("Camera error", e)
                return np.zeros((928, 1664), dtype=np.uint8)
        img = np.empty((int(1664 * 928 * 1.5),), dtype=np.uint8)
        try:
            self.camera.capture(img, format='yuv', use_video_port=True, resize=None)
        except Exception as e:
            print("Camera error", e)
        yChannelSize = int(1664 * 928)
        img = img[0:yChannelSize].reshape((928, 1664))
        return np.copy(img)

    def getOpticalAngleMarkerImage(self):
        if _is_pi5():
            try:
                arr = self.camera._cam.capture_array('main')
                return arr
            except Exception as e:
                print("Camera error", e)
                return np.zeros((928, 1648, 3), dtype=np.uint8)
        img = None
        try:
            img = np.empty((1648 * 928 * 3,), dtype=np.uint8)
            self.camera.capture(img, format='bgr', use_video_port=True, resize=None)
        except Exception as e:
            print("Camera error", e)
        img = img.reshape((928, 1648, 3))
        return img

    def getScanImageStack(self):
        if constants.Scanning.RESIZE is None:
            w = self.CAMERA_RES[0]
            h = self.CAMERA_RES[1]
        else:
            w = constants.Scanning.RESIZE[0]
            h = constants.Scanning.RESIZE[1]

        if _is_pi5():
            stackFrames = []
            for _ in range(constants.Scanning.IMAGE_STACK):
                arr = self.camera._cam.capture_array('main')
                stackFrames.append(arr[:h, :w].copy() if arr.ndim == 2 else arr[:h, :w, 0].copy())
            if len(stackFrames) == 1:
                return stackFrames[0].astype(np.uint8)
            sumImage = np.mean(np.stack(stackFrames, axis=0), axis=0)
            return sumImage.astype(np.uint8)

        imageList = []
        for i in range(constants.Scanning.IMAGE_STACK):
            imageList.append(np.empty((int(h * w * 1.5),), dtype=np.uint8))
        try:
            self.camera.capture_sequence(imageList, format='yuv', use_video_port=True,
                                         resize=constants.Scanning.RESIZE)
        except Exception as e:
            print("Camera error", e)
        yChannelSize = int(h * w)
        sumImage = imageList[0][0:yChannelSize].reshape((h, w))
        if len(imageList) > 1:
            sumImage = sumImage.astype(np.float32)
            for i in range(1, len(imageList)):
                sumImage += imageList[i][0:yChannelSize].reshape((h, w)).astype(np.float32)
            sumImage = sumImage / constants.Scanning.IMAGE_STACK
        return sumImage.astype(np.uint8)

    def captureColourImageStack(self):
        if constants.Scanning.RESIZE is None:
            w = self.CAMERA_RES[0]
            h = self.CAMERA_RES[1]
        else:
            w = constants.Scanning.RESIZE[0]
            h = constants.Scanning.RESIZE[1]

        if _is_pi5():
            stackFrames = []
            for _ in range(constants.Scanning.IMAGE_STACK):
                arr = self.camera._cam.capture_array('main')
                stackFrames.append(arr[:h, :w, :3].copy())
            if len(stackFrames) == 1:
                return stackFrames[0].astype(np.uint8)
            sumImage = np.mean(np.stack(stackFrames, axis=0), axis=0)
            return sumImage.astype(np.uint8)

        imageList = []
        for i in range(constants.Scanning.IMAGE_STACK):
            imageList.append(np.empty((w * h * 3,), dtype=np.uint8))
        try:
            self.camera.capture_sequence(imageList, format='bgr', use_video_port=True,
                                         resize=constants.Scanning.RESIZE)
        except Exception as e:
            print("Camera error", e)
        sumImage = imageList[0].reshape((h, w, 3))
        if len(imageList) > 1:
            sumImage = sumImage.astype(np.float32)
            for i in range(1, len(imageList)):
                sumImage += imageList[i].reshape((h, w, 3)).astype(np.float32)
            sumImage = sumImage / constants.Scanning.IMAGE_STACK
        return sumImage.astype(np.uint8)

    def captureColourJPG(self):
        try:
            mStream = io.BytesIO()
            if _is_pi5():
                self.camera._cam.capture_file(mStream, format='jpeg')
            else:
                self.camera.capture(mStream, format='jpeg', use_video_port=True,
                                    resize=constants.Scanning.RESIZE,
                                    quality=constants.Scanning.JPG_QUALITY)
        except Exception as e:
            print("Camera error", e)
            return None
        return mStream

    def startVideoAndProcessing(self, mode='yuv'):
        rt = self._get_realtime()
        if rt is None:
            return
        try:
            if self.camera.recording:
                self.stopVideo()
            if _is_pi5():
                # picamera2 always uses MJPEG encoder for the streaming path
                self.camera.start_recording(rt, format='mjpeg',
                                            bitrate=constants.Scanning.BIT_RATE,
                                            resize=constants.Scanning.RESIZE)
                self.currentBitRate = constants.Scanning.BIT_RATE
            else:
                if mode == 'yuv':
                    self.camera.start_recording(rt, format='yuv',
                                                resize=constants.Scanning.RESIZE)
                if mode == 'mjpeg':
                    self.camera.start_recording(rt, format='mjpeg',
                                                bitrate=constants.Scanning.BIT_RATE,
                                                resize=constants.Scanning.RESIZE)
                    self.currentBitRate = constants.Scanning.BIT_RATE
            print('start_recording')
        except Exception as e:
            print("Camera video error:", e)
        return True

    def stopVideo(self):
        try:
            self.camera.stop_recording()
            print('stop_recording')
        except Exception as e:
            print("Camera video error:", e)
        return True

    def wait(self, seconds):
        try:
            self.camera.wait_recording(seconds)
        except Exception as e:
            print("Camera video error:", e)
            return False
        return True


