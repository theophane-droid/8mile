import sys
import os
import argparse

import pandas as pd

from datetime import datetime

import sys
from Hmile.DataRenderer import TensorboardDataRenderer
from Hmile.Exception import DataframeFormatException, EmptyDataRendererException
from random import randint

import unittest


class FullTestTensorBoardRenderer(unittest.TestCase):
    def setUp(self):
    # parse args to get data_path and logs_dir
        data = pd.read_csv('test/data/data.csv')

        # create renderer
        renderer = TensorboardDataRenderer(
            'logs/',
            activate_rew=True
        )
        self.fill_renderer(data, renderer)
        self.renderer = renderer
        self.data = data
    
    def fill_renderer(self, data, renderer):
        for index, row in data.iterrows():
            date = datetime.strptime(row["Date"], "%Y-%m-%d")
            renderer.append("open", row["open"], date)
            renderer.append("close", row["close"], date)
            renderer.append("high", row["high"], date)
            renderer.append("low", row["low"], date)
            renderer.append("volume", row["volume"], date)
            renderer.append("exit", row["exit"], date)
            renderer.append("long", row["long"], date)
            renderer.append("short", row["short"], date)
            renderer.append("money", row["money"], date)
            renderer.append("rew", randint(1,100), date)
    
    def test_renderer(self):
        self.fill_renderer(self.data, self.renderer)
        self.renderer.render()
    
    def test_next_step(self):
        self.renderer.next_step()
        self.fill_renderer(self.data, self.renderer)
        self.renderer.render()

class OHLCVTestTensorBoardRenderer(unittest.TestCase):
    def setUp(self):
    # parse args to get data_path and logs_dir
        data = pd.read_csv('test/data/data.csv')

        # create renderer
        renderer = TensorboardDataRenderer(
            'logs/',
            activate_rew=True
        )
        self.fill_renderer(data, renderer)
        self.renderer = renderer
        self.data = data
    
    def fill_renderer(self, data, renderer):
        for index, row in data.iterrows():
            date = datetime.strptime(row["Date"], "%Y-%m-%d")
            renderer.append("open", row["open"], date)
            renderer.append("close", row["close"], date)
            renderer.append("high", row["high"], date)
            renderer.append("low", row["low"], date)
            renderer.append("volume", row["volume"], date)
    
    def test_renderer(self):
        self.fill_renderer(self.data, self.renderer)
        self.renderer.render()


class MissingColsTensorBoardRenderer(unittest.TestCase):
    def setUp(self):
    # parse args to get data_path and logs_dir
        data = pd.read_csv('test/data/data.csv')

        # create renderer
        renderer = TensorboardDataRenderer(
            'logs/'
        )
        self.fill_renderer(data, renderer)
        self.renderer = renderer
        self.data = data
    
    def fill_renderer(self, data, renderer):
        for index, row in data.iterrows():
            date = datetime.strptime(row["Date"], "%Y-%m-%d")
            renderer.append("open", row["open"], date)
            renderer.append("close", row["close"], date)
            renderer.append("high", row["high"], date)
            renderer.append("low", row["low"], date)
            if index % 2 == 0:
                renderer.append("volume", row["volume"], date)
    
    def test_renderer(self):
        self.fill_renderer(self.data, self.renderer)
        with self.assertRaises(DataframeFormatException):
            self.renderer.render()


class EmptyDataDrameTest(unittest.TestCase):
    def setUp(self):
        self.renderer = TensorboardDataRenderer(
            'logs/',
            activate_rew=True
        )
    
    def test(self):
        with self.assertRaises(EmptyDataRendererException):
            self.renderer.render()