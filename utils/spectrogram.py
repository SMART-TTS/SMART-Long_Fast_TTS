import librosa
import numpy as np


def logmelspec(audiopath, sampling_rate, n_mel, n_fft, hop_length, win_length, audio_refdB, audio_maxdB, audio=None):
    if audio is None:
        audio, rate = librosa.core.load(audiopath, sr=sampling_rate)
        audio = 0.95 * librosa.util.normalize(audio)
    spec = librosa.stft(y=audio,
                        n_fft=int(n_fft),
                        hop_length=int(hop_length),
                        win_length=int(win_length))
    spec = np.absolute(spec)
    mel_filters = librosa.filters.mel(sampling_rate, n_fft, n_mel)
    mel = np.dot(mel_filters, spec)
    # to dB
    mel[mel < 1e-10] = 1e-10
    mel = 20 * np.log10(mel)
    # normalize
    mel = np.clip((mel - audio_refdB + audio_maxdB) / audio_maxdB, 1e-8, 1)
    return mel


# def stft(x, n_fft, n_shift, win_length=None, window='hann', center=True,
#          pad_mode='reflect'):
#     # x: [Time, Channel]
#     if x.ndim == 1:
#         single_channel = True
#         # x: [Time] -> [Time, Channel]
#         x = x[:, None]
#     else:
#         single_channel = False
#     x = x.astype(np.float32)
#
#     # FIXME(kamo): librosa.stft can't use multi-channel?
#     # x: [Time, Channel, Freq]
#     x = np.stack([librosa.stft(
#         x[:, ch],
#         n_fft=n_fft,
#         hop_length=n_shift,
#         win_length=win_length,
#         window=window,
#         center=center,
#         pad_mode=pad_mode).T
#         for ch in range(x.shape[1])], axis=1)
#
#     if single_channel:
#         # x: [Time, Channel, Freq] -> [Time, Freq]
#         x = x[:, 0]
#     return x
#
#
# def istft(x, n_shift, win_length=None, window='hann', center=True):
#     # x: [Time, Channel, Freq]
#     if x.ndim == 2:
#         single_channel = True
#         # x: [Time, Freq] -> [Time, Channel, Freq]
#         x = x[:, None, :]
#     else:
#         single_channel = False
#
#     # x: [Time, Channel]
#     x = np.stack([librosa.istft(
#         x[:, ch].T,  # [Time, Freq] -> [Freq, Time]
#         hop_length=n_shift,
#         win_length=win_length,
#         window=window,
#         center=center)
#         for ch in range(x.shape[1])], axis=1)
#
#     if single_channel:
#         # x: [Time, Channel] -> [Time]
#         x = x[:, 0]
#     return x
#
#
# def stft2logmelspectrogram(x_stft, fs, n_mels, n_fft, fmin=None, fmax=None,
#                            eps=1e-10, use_norm=True):
#     # x_stft: (Time, Channel, Freq) or (Time, Freq)
#     fmin = 0 if fmin is None else fmin
#     fmax = fs / 2 if fmax is None else fmax
#
#     # spc: (Time, Channel, Freq) or (Time, Freq)
#     spc = np.abs(x_stft)
#     # mel_basis: (Mel_freq, Freq)
#     mel_basis = librosa.filters.mel(fs, n_fft, n_mels, fmin, fmax)
#     # lmspc: (Time, Channel, Mel_freq) or (Time, Mel_freq)
#     if use_norm:
#         lmspc = 20 * np.log10(np.maximum(eps, np.dot(spc, mel_basis.T)))
#         lmspc = np.clip((lmspc - 20 + 100) / 100, 1e-8, 1)
#     else:
#         lmspc = np.log10(np.maximum(eps, np.dot(spc, mel_basis.T)))
#
#     return lmspc
#
#
# def spectrogram(x, n_fft, n_shift, win_length=None, window='hann', use_norm=True):
#     # x: (Time, Channel) -> spc: (Time, Channel, Freq)
#     spc = np.abs(stft(x, n_fft, n_shift, win_length, window=window))
#     if use_norm:
#         spc = 20 * np.log10(np.maximum(1e-10, spc))
#         spc = np.clip((spc - 20 + 100) / 100, 1e-8, 1)
#     return spc
#
#
# def logmelspectrogram(x, fs, n_mels, n_fft, n_shift,
#                       win_length=None, window='hann', fmin=None, fmax=None,
#                       eps=1e-10, pad_mode='reflect'):
#     # stft: (Time, Channel, Freq) or (Time, Freq)
#     x_stft = stft(x, n_fft=n_fft, n_shift=n_shift, win_length=win_length,
#                   window=window, pad_mode=pad_mode)
#
#     return stft2logmelspectrogram(x_stft, fs=fs, n_mels=n_mels, n_fft=n_fft,
#                                   fmin=fmin, fmax=fmax, eps=eps)
#
#
# class Spectrogram(object):
#     def __init__(self, n_fft, n_shift, win_length=None, window='hann'):
#         self.n_fft = n_fft
#         self.n_shift = n_shift
#         self.win_length = win_length
#         self.window = window
#
#     def __repr__(self):
#         return ('{name}(n_fft={n_fft}, n_shift={n_shift}, '
#                 'win_length={win_length}, window={window})'
#                 .format(name=self.__class__.__name__,
#                         n_fft=self.n_fft,
#                         n_shift=self.n_shift,
#                         win_length=self.win_length,
#                         window=self.window))
#
#     def __call__(self, x):
#         return spectrogram(x,
#                            n_fft=self.n_fft, n_shift=self.n_shift,
#                            win_length=self.win_length,
#                            window=self.window)
#
#
# class LogMelSpectrogram(object):
#     def __init__(self, fs, n_mels, n_fft, n_shift, win_length=None,
#                  window='hann', fmin=None, fmax=None, eps=1e-10):
#         self.fs = fs
#         self.n_mels = n_mels
#         self.n_fft = n_fft
#         self.n_shift = n_shift
#         self.win_length = win_length
#         self.window = window
#         self.fmin = fmin
#         self.fmax = fmax
#         self.eps = eps
#
#     def __repr__(self):
#         return ('{name}(fs={fs}, n_mels={n_mels}, n_fft={n_fft}, '
#                 'n_shift={n_shift}, win_length={win_length}, window={window}, '
#                 'fmin={fmin}, fmax={fmax}, eps={eps}))'
#                 .format(name=self.__class__.__name__,
#                         fs=self.fs,
#                         n_mels=self.n_mels,
#                         n_fft=self.n_fft,
#                         n_shift=self.n_shift,
#                         win_length=self.win_length,
#                         window=self.window,
#                         fmin=self.fmin,
#                         fmax=self.fmax,
#                         eps=self.eps))
#
#     def __call__(self, x):
#         return logmelspectrogram(
#             x,
#             fs=self.fs,
#             n_mels=self.n_mels,
#             n_fft=self.n_fft, n_shift=self.n_shift,
#             win_length=self.win_length,
#             window=self.window)
#
#
# class Stft2LogMelSpectrogram(object):
#     def __init__(self, fs, n_mels, n_fft, fmin=None, fmax=None, eps=1e-10):
#         self.fs = fs
#         self.n_mels = n_mels
#         self.n_fft = n_fft
#         self.fmin = fmin
#         self.fmax = fmax
#         self.eps = eps
#
#     def __repr__(self):
#         return ('{name}(fs={fs}, n_mels={n_mels}, n_fft={n_fft}, '
#                 'fmin={fmin}, fmax={fmax}, eps={eps}))'
#                 .format(name=self.__class__.__name__,
#                         fs=self.fs,
#                         n_mels=self.n_mels,
#                         n_fft=self.n_fft,
#                         fmin=self.fmin,
#                         fmax=self.fmax,
#                         eps=self.eps))
#
#     def __call__(self, x):
#         return stft2logmelspectrogram(
#             x,
#             fs=self.fs,
#             n_mels=self.n_mels,
#             n_fft=self.n_fft,
#             fmin=self.fmin,
#             fmax=self.fmax)
#
#
# class Stft(object):
#     def __init__(self, n_fft, n_shift, win_length=None,
#                  window='hann', center=True, pad_mode='reflect'):
#         self.n_fft = n_fft
#         self.n_shift = n_shift
#         self.win_length = win_length
#         self.window = window
#         self.center = center
#         self.pad_mode = pad_mode
#
#     def __repr__(self):
#         return ('{name}(n_fft={n_fft}, n_shift={n_shift}, '
#                 'win_length={win_length}, window={window},'
#                 'center={center}, pad_mode={pad_mode})'
#                 .format(name=self.__class__.__name__,
#                         n_fft=self.n_fft,
#                         n_shift=self.n_shift,
#                         win_length=self.win_length,
#                         window=self.window,
#                         center=self.center,
#                         pad_mode=self.pad_mode))
#
#     def __call__(self, x):
#         return stft(x, self.n_fft, self.n_shift,
#                     win_length=self.win_length,
#                     window=self.window,
#                     center=self.center,
#                     pad_mode=self.pad_mode)
#
#
# class IStft(object):
#     def __init__(self, n_shift, win_length=None, window='hann', center=True):
#         self.n_shift = n_shift
#         self.win_length = win_length
#         self.window = window
#         self.center = center
#
#     def __repr__(self):
#         return ('{name}(n_shift={n_shift}, '
#                 'win_length={win_length}, window={window},'
#                 'center={center})'
#                 .format(name=self.__class__.__name__,
#                         n_shift=self.n_shift,
#                         win_length=self.win_length,
#                         window=self.window,
#                         center=self.center))
#
#     def __call__(self, x):
#         return istft(x, self.n_shift,
#                      win_length=self.win_length,
#                      window=self.window,
#                      center=self.center)
