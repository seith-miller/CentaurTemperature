#!/usr/bin/env python3
from aws_cdk import App
from temperature_monitor_stack import TemperatureMonitorStack

app = App()
TemperatureMonitorStack(app, "TemperatureMonitorStack")
app.synth()
