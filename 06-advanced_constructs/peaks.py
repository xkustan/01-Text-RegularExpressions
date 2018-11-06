import numpy
import sys
import struct
import wave

P = 1  # P is the (time) length of the analysis window in seconds

# nice solution, but printing warnings to output
# from scipy.io import wavfile
# def read_wav_with_wavfile(file_path):
#     fr, data = wavfile.read(file_path)
#
#     if type(data[0]) == numpy.ndarray:  # stereo
#         mono_data = []
#         for cycle in data:
#             mono_data.append(numpy.mean(cycle))
#
#         return numpy.array(mono_data), fr
#
#     elif type(data[0]) == numpy.int16:  # mono
#         return data, fr
#     else:
#         raise Exception("Invalid format, use PCM 16bit mono or stereo!")


def read_wav(file_path):
    with wave.open(file_path, mode="rb") as wav_file:
        channels = wav_file.getnchannels()
        frames = wav_file.getnframes()
        fr = wav_file.getframerate()

        raw_data = wav_file.readframes(nframes=frames)

        wav_file.close()

    wav_iter = struct.iter_unpack("h", raw_data)

    samples = []

    for x in wav_iter:
        if channels == 1:
            samples.append(x[0])
        elif channels == 2:
            y = wav_iter.__next__()
            avg_stereo = (x[0] + y[0]) / 2
            samples.append(avg_stereo)
        else:
            sys.exit("Too many channels.")

    return numpy.array(samples), fr


def generate_chunks(data, size):
    full_length = len(data)
    number_of_samples = full_length // size

    for i in range(0, full_length, size):
        number_of_samples -= 1
        if number_of_samples >= 0:
            yield data[i:i+size]


def analyse_wav(data, frame_rate):
    high = numpy.NINF
    low = numpy.inf

    chunk_size = P * frame_rate

    for chunk in generate_chunks(data, chunk_size):
        ft = numpy.fft.rfft(chunk)
        ft = numpy.abs(ft)
        average_amplitude = numpy.mean(ft)
        threshold_amplitude = 20 * average_amplitude
        peaks = numpy.argwhere(ft >= threshold_amplitude)
        if len(peaks):
            tmp_min_peak = peaks.min()
            tmp_max_peak = peaks.max()
            if tmp_min_peak < low:
                low = tmp_min_peak
            if tmp_max_peak > high:
                high = tmp_max_peak

    if numpy.isfinite(high) or numpy.isfinite(low):
        print("low = {}, high = {}".format(low, high))
    else:
        print("no peaks")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Argument has to be path to valid audio file in wav format!")

    filename = sys.argv[1]
    wav_data, frame_rate = read_wav(filename)
    analyse_wav(wav_data, frame_rate)
