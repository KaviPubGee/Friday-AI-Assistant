from pycaw.pycaw import AudioUtilities

def test():
    devices = AudioUtilities.GetSpeakers()
    volume = devices.EndpointVolume
    print(dir(volume))
    print("Mute status:", volume.GetMute())

test()
