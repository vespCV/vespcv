import os
import cv2
import torch
import numpy as np
from ultralytics import YOLO
import time
import subprocess

from detector import load_config, create_model