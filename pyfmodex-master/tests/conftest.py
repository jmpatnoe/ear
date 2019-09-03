import os
import pyfmodex
import pytest
from pyfmodex.enums import DSP_TYPE, DSPCONNECTION_TYPE

@pytest.fixture()
def many_speakers_system():
    system = pyfmodex.System()
    format = system.software_format
    format.speaker_mode = 7
    system.software_format = format
    yield system

@pytest.fixture(scope="session")
def system():
    system = pyfmodex.System()
    yield system
    system.release()

@pytest.fixture(scope="session")
def initialized_system():
    system = pyfmodex.System()
    system.init()
    yield system
    system.close()
    system.release()

@pytest.fixture
def sound(initialized_system):
    sound = initialized_system.create_sound(os.path.join(os.path.dirname(__file__), "test.fsb"))
    yield sound
    sound.release()

@pytest.fixture
def channel(sound):
    channel = sound.get_subsound(0).play(paused=True)
    return channel

@pytest.fixture(scope="session")
def midi_sound(initialized_system):
    sound = initialized_system.create_sound(os.path.join(os.path.dirname(__file__), "innerlight.mid"))
    yield sound
    sound.release()

@pytest.fixture
def echo(initialized_system):
    return initialized_system.create_dsp_by_type(DSP_TYPE.ECHO)

@pytest.fixture
def channel_group(initialized_system, channel):
    group = initialized_system.create_channel_group("test group")
    channel.channel_group = group
    return group

@pytest.fixture
def sound_group(initialized_system):
    group = initialized_system.create_sound_group("test group")
    return group

@pytest.fixture
def compressor(initialized_system):
    comp = initialized_system.create_dsp_by_type(DSP_TYPE.COMPRESSOR)
    return comp

@pytest.fixture
def oscillator(initialized_system):
    osc = initialized_system.create_dsp_by_type(DSP_TYPE.OSCILLATOR)
    return osc

@pytest.fixture
def conn(echo, oscillator):
    conn = echo.add_input(echo, DSPCONNECTION_TYPE.STANDARD)
    return conn

@pytest.fixture
def geometry(initialized_system):
    geom = initialized_system.create_geometry(42, 420)
    return geom

@pytest.fixture
def reverb(initialized_system):
    reverb = initialized_system.create_reverb_3d()
    return reverb