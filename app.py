from gradio import TabbedInterface

from demo.delightful_hifi import interfaceDelightfulHifi44100
from demo.delightful_univnet import interfaceDelightfulUnuvnet22050
from demo.fastpitch_hifi import interfaceFastpichHifi

TabbedInterface(
    [
        interfaceDelightfulUnuvnet22050,
        interfaceDelightfulHifi44100,
        interfaceFastpichHifi,
    ],
    ["DelightfulUnuvnet", "DelightfulHifi", "FastpichHifi"],
).launch()
