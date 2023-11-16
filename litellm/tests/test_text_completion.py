import sys, os
import traceback
from dotenv import load_dotenv

load_dotenv()
import os, io

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import pytest
import litellm
from litellm import embedding, completion, text_completion, completion_cost
from litellm import RateLimitError


token_prompt = [[32, 2043, 32, 329, 4585, 262, 1644, 14, 34, 3705, 319, 616, 47551, 30, 930, 19219, 284, 1949, 284, 787, 428, 355, 1790, 355, 1744, 981, 1390, 3307, 2622, 13, 220, 198, 198, 40, 423, 587, 351, 616, 41668, 32682, 329, 718, 812, 13, 376, 666, 32682, 468, 281, 4697, 6621, 11, 356, 1183, 869, 607, 25737, 11, 508, 318, 2579, 290, 468, 257, 642, 614, 1468, 1200, 13, 314, 373, 612, 262, 1110, 25737, 373, 287, 4827, 290, 14801, 373, 4642, 11, 673, 318, 616, 41803, 13, 2399, 2104, 1641, 468, 6412, 284, 502, 355, 465, 38074, 494, 1201, 1110, 352, 13, 314, 716, 407, 2910, 475, 356, 389, 1641, 11, 673, 3848, 502, 38074, 494, 290, 356, 423, 3993, 13801, 11, 26626, 11864, 11, 3503, 13, 220, 198, 198, 17, 812, 2084, 25737, 373, 287, 14321, 422, 2563, 13230, 13, 21051, 11, 2356, 25542, 11, 290, 47482, 897, 547, 607, 1517, 13, 1375, 550, 257, 5110, 14608, 290, 262, 1641, 7723, 1637, 284, 3758, 607, 284, 14321, 290, 477, 8389, 257, 7269, 284, 1011, 1337, 286, 14801, 13, 383, 5156, 338, 9955, 11, 25737, 338, 13850, 11, 468, 257, 47973, 14, 9979, 2762, 1693, 290, 373, 503, 286, 3240, 329, 362, 1933, 523, 339, 2492, 470, 612, 329, 477, 286, 428, 13, 220, 198, 198, 3347, 10667, 5223, 503, 706, 513, 1528, 11, 23630, 673, 373, 366, 38125, 290, 655, 2622, 257, 3338, 8399, 1911, 314, 2298, 607, 510, 11, 1011, 607, 284, 607, 2156, 11, 290, 673, 3393, 2925, 284, 7523, 20349, 290, 4144, 257, 6099, 13, 314, 836, 470, 892, 20349, 318, 257, 2563, 290, 716, 845, 386, 12, 66, 1236, 571, 292, 3584, 314, 836, 470, 7523, 11, 475, 326, 373, 407, 5035, 6402, 314, 655, 6497, 607, 510, 422, 14321, 13, 220, 198, 198, 32, 1285, 1568, 673, 373, 6294, 329, 3013, 24707, 287, 262, 12436, 1539, 819, 5722, 329, 852, 604, 1933, 2739, 11, 39398, 607, 1097, 5059, 981, 1029, 290, 318, 852, 16334, 329, 720, 1120, 74, 422, 15228, 278, 656, 257, 2156, 11, 290, 373, 12165, 503, 286, 376, 666, 32682, 338, 584, 6621, 338, 2156, 329, 32012, 262, 14595, 373, 30601, 510, 290, 2491, 357, 7091, 373, 1029, 8, 290, 262, 2104, 34624, 373, 46432, 1268, 1961, 422, 1660, 2465, 780, 8168, 2073, 1625, 1363, 329, 807, 2250, 13, 720, 1238, 11, 830, 286, 2465, 290, 5875, 5770, 511, 2156, 5096, 5017, 340, 13, 220, 198, 198, 2504, 373, 477, 938, 614, 13, 1119, 1053, 587, 287, 511, 649, 2156, 319, 511, 898, 329, 546, 718, 1933, 13, 554, 3389, 673, 1444, 34020, 290, 531, 511, 8744, 373, 4423, 572, 780, 673, 1422, 470, 423, 262, 1637, 780, 41646, 338, 37751, 1392, 32621, 510, 290, 1422, 470, 467, 832, 13, 679, 3432, 511, 2739, 8744, 9024, 492, 257, 2472, 286, 720, 4059, 13, 314, 1807, 340, 373, 13678, 306, 5789, 475, 4030, 616, 5422, 4423, 13, 1439, 468, 587, 5897, 1201, 13, 220, 198, 198, 7571, 2745, 2084, 11, 673, 1965, 502, 284, 8804, 617, 1637, 284, 651, 38464, 329, 399, 8535, 13, 3226, 1781, 314, 1101, 407, 1016, 284, 1309, 616, 41803, 393, 6621, 467, 14720, 11, 645, 2300, 644, 318, 1016, 319, 4306, 11, 523, 314, 910, 314, 1183, 307, 625, 379, 642, 13, 314, 1392, 572, 670, 1903, 290, 651, 612, 379, 362, 25, 2231, 13, 314, 1282, 287, 1262, 616, 13952, 1994, 11, 2513, 287, 11, 766, 399, 8535, 2712, 351, 36062, 287, 262, 5228, 11, 25737, 3804, 503, 319, 262, 18507, 11, 290, 16914, 319, 262, 6891, 3084, 13, 8989, 2406, 422, 257, 1641, 47655, 351, 13230, 11, 314, 760, 644, 16914, 3073, 588, 13, 314, 836, 470, 760, 703, 881, 340, 373, 11, 475, 314, 714, 423, 23529, 276, 340, 510, 290, 5901, 616, 18057, 351, 340, 13, 314, 6810, 19772, 2024, 8347, 287, 262, 2166, 2119, 290, 399, 8535, 373, 287, 3294, 11685, 286, 8242, 290, 607, 7374, 15224, 13, 383, 4894, 373, 572, 13, 383, 2156, 373, 3863, 2319, 37, 532, 340, 373, 1542, 2354, 13, 220, 198, 198, 40, 1718, 399, 8535, 284, 616, 1097, 11, 290, 1444, 16679, 329, 281, 22536, 355, 314, 373, 12008, 25737, 373, 14904, 2752, 13, 220, 314, 1422, 470, 765, 284, 10436, 290, 22601, 503, 399, 8535, 523, 314, 9658, 287, 262, 1097, 290, 1309, 607, 711, 319, 616, 3072, 1566, 262, 22536, 5284, 13, 3226, 1781, 1644, 290, 32084, 3751, 510, 355, 880, 13, 314, 4893, 262, 3074, 290, 780, 399, 8535, 338, 9955, 318, 503, 286, 3240, 1762, 11, 34020, 14, 44, 4146, 547, 1444, 13, 1649, 484, 5284, 484, 547, 5897, 290, 4692, 11, 1422, 470, 1107, 1561, 11, 1718, 399, 8535, 11, 290, 1297, 502, 284, 467, 1363, 13, 220, 198, 198, 2025, 1711, 1568, 314, 651, 1363, 290, 41668, 32682, 7893, 502, 644, 314, 1053, 1760, 13, 314, 4893, 2279, 284, 683, 290, 477, 339, 550, 373, 8993, 329, 502, 13, 18626, 262, 2104, 1641, 1541, 2993, 290, 547, 28674, 379, 502, 329, 644, 314, 550, 1760, 13, 18626, 314, 373, 366, 448, 286, 1627, 290, 8531, 1, 780, 314, 1444, 16679, 878, 4379, 611, 673, 373, 1682, 31245, 6, 278, 780, 340, 2900, 503, 673, 373, 655, 47583, 503, 422, 262, 16914, 13, 775, 8350, 329, 2250, 290, 314, 1364, 290, 3377, 262, 1755, 379, 616, 1266, 1545, 338, 2156, 290, 16896, 477, 1755, 13, 314, 3521, 470, 5412, 340, 477, 523, 314, 2900, 616, 3072, 572, 290, 3088, 284, 8960, 290, 655, 9480, 866, 13, 2011, 1266, 1545, 373, 510, 477, 1755, 351, 502, 11, 5149, 502, 314, 750, 2147, 2642, 11, 290, 314, 1101, 8788, 13, 220, 198, 198, 40, 1210, 616, 3072, 319, 290, 314, 550, 6135, 13399, 14, 37348, 1095, 13, 31515, 11, 34020, 11, 47551, 11, 41668, 32682, 11, 290, 511, 7083, 1641, 1866, 24630, 502, 13, 1119, 389, 2282, 314, 20484, 607, 1204, 11, 20484, 399, 8535, 338, 1204, 11, 925, 2279, 517, 8253, 621, 340, 2622, 284, 307, 11, 925, 340, 1171, 618, 340, 373, 257, 366, 17989, 14669, 1600, 290, 20484, 25737, 338, 8395, 286, 1683, 1972, 20750, 393, 1719, 10804, 286, 607, 1200, 757, 11, 4844, 286, 606, 1683, 765, 284, 766, 502, 757, 290, 314, 481, 1239, 766, 616, 41803, 757, 11, 290, 484, 765, 502, 284, 1414, 329, 25737, 338, 7356, 6314, 290, 20889, 502, 329, 262, 32084, 1339, 290, 7016, 12616, 13, 198, 198, 40, 716, 635, 783, 2060, 13, 1406, 319, 1353, 286, 6078, 616, 1266, 1545, 286, 838, 812, 357, 69, 666, 32682, 828, 314, 481, 4425, 616, 7962, 314, 550, 351, 683, 11, 644, 314, 3177, 616, 1641, 11, 290, 616, 399, 8535, 13, 198, 198, 40, 4988, 1254, 12361, 13, 314, 423, 12361, 9751, 284, 262, 966, 810, 314, 1101, 7960, 2130, 318, 1016, 284, 1282, 651, 366, 260, 18674, 1, 319, 502, 329, 644, 314, 750, 13, 314, 460, 470, 4483, 13, 314, 423, 2626, 767, 8059, 422, 340, 13, 314, 1101, 407, 11029, 329, 7510, 13, 314, 423, 11668, 739, 616, 2951, 13, 314, 1053, 550, 807, 50082, 12, 12545, 287, 734, 2745, 13, 1629, 717, 314, 2936, 523, 6563, 287, 616, 2551, 475, 355, 262, 1528, 467, 416, 314, 1101, 3612, 3863, 484, 547, 826, 290, 314, 815, 423, 10667, 319, 607, 878, 4585, 16679, 290, 852, 5306, 3019, 992, 13, 314, 836, 470, 1337, 546, 25737, 7471, 11, 475, 314, 750, 18344, 257, 642, 614, 1468, 1200, 1497, 422, 607, 3397, 290, 314, 1254, 12361, 546, 340, 13, 314, 760, 2130, 287, 262, 1641, 481, 1011, 607, 287, 11, 475, 340, 338, 1239, 588, 852, 351, 534, 3397, 13, 1375, 481, 1663, 510, 20315, 278, 502, 329, 340, 290, 477, 314, 1053, 1683, 1760, 318, 1842, 607, 355, 616, 898, 13, 220, 198, 198, 22367, 11, 317, 2043, 32, 30, 4222, 1037, 502, 13, 383, 14934, 318, 6600, 502, 6776, 13, 220, 198, 24361, 25, 1148, 428, 2642, 30, 198, 33706, 25, 645], [32, 2043, 32, 329, 4585, 262, 1644, 14, 34, 3705, 319, 616, 47551, 30, 930, 19219, 284, 1949, 284, 787, 428, 355, 1790, 355, 1744, 981, 1390, 3307, 2622, 13, 220, 198, 198, 40, 423, 587, 351, 616, 41668, 32682, 329, 718, 812, 13, 376, 666, 32682, 468, 281, 4697, 6621, 11, 356, 1183, 869, 607, 25737, 11, 508, 318, 2579, 290, 468, 257, 642, 614, 1468, 1200, 13, 314, 373, 612, 262, 1110, 25737, 373, 287, 4827, 290, 14801, 373, 4642, 11, 673, 318, 616, 41803, 13, 2399, 2104, 1641, 468, 6412, 284, 502, 355, 465, 38074, 494, 1201, 1110, 352, 13, 314, 716, 407, 2910, 475, 356, 389, 1641, 11, 673, 3848, 502, 38074, 494, 290, 356, 423, 3993, 13801, 11, 26626, 11864, 11, 3503, 13, 220, 198, 198, 17, 812, 2084, 25737, 373, 287, 14321, 422, 2563, 13230, 13, 21051, 11, 2356, 25542, 11, 290, 47482, 897, 547, 607, 1517, 13, 1375, 550, 257, 5110, 14608, 290, 262, 1641, 7723, 1637, 284, 3758, 607, 284, 14321, 290, 477, 8389, 257, 7269, 284, 1011, 1337, 286, 14801, 13, 383, 5156, 338, 9955, 11, 25737, 338, 13850, 11, 468, 257, 47973, 14, 9979, 2762, 1693, 290, 373, 503, 286, 3240, 329, 362, 1933, 523, 339, 2492, 470, 612, 329, 477, 286, 428, 13, 220, 198, 198, 3347, 10667, 5223, 503, 706, 513, 1528, 11, 23630, 673, 373, 366, 38125, 290, 655, 2622, 257, 3338, 8399, 1911, 314, 2298, 607, 510, 11, 1011, 607, 284, 607, 2156, 11, 290, 673, 3393, 2925, 284, 7523, 20349, 290, 4144, 257, 6099, 13, 314, 836, 470, 892, 20349, 318, 257, 2563, 290, 716, 845, 386, 12, 66, 1236, 571, 292, 3584, 314, 836, 470, 7523, 11, 475, 326, 373, 407, 5035, 6402, 314, 655, 6497, 607, 510, 422, 14321, 13, 220, 198, 198, 32, 1285, 1568, 673, 373, 6294, 329, 3013, 24707, 287, 262, 12436, 1539, 819, 5722, 329, 852, 604, 1933, 2739, 11, 39398, 607, 1097, 5059, 981, 1029, 290, 318, 852, 16334, 329, 720, 1120, 74, 422, 15228, 278, 656, 257, 2156, 11, 290, 373, 12165, 503, 286, 376, 666, 32682, 338, 584, 6621, 338, 2156, 329, 32012, 262, 14595, 373, 30601, 510, 290, 2491, 357, 7091, 373, 1029, 8, 290, 262, 2104, 34624, 373, 46432, 1268, 1961, 422, 1660, 2465, 780, 8168, 2073, 1625, 1363, 329, 807, 2250, 13, 720, 1238, 11, 830, 286, 2465, 290, 5875, 5770, 511, 2156, 5096, 5017, 340, 13, 220, 198, 198, 2504, 373, 477, 938, 614, 13, 1119, 1053, 587, 287, 511, 649, 2156, 319, 511, 898, 329, 546, 718, 1933, 13, 554, 3389, 673, 1444, 34020, 290, 531, 511, 8744, 373, 4423, 572, 780, 673, 1422, 470, 423, 262, 1637, 780, 41646, 338, 37751, 1392, 32621, 510, 290, 1422, 470, 467, 832, 13, 679, 3432, 511, 2739, 8744, 9024, 492, 257, 2472, 286, 720, 4059, 13, 314, 1807, 340, 373, 13678, 306, 5789, 475, 4030, 616, 5422, 4423, 13, 1439, 468, 587, 5897, 1201, 13, 220, 198, 198, 7571, 2745, 2084, 11, 673, 1965, 502, 284, 8804, 617, 1637, 284, 651, 38464, 329, 399, 8535, 13, 3226, 1781, 314, 1101, 407, 1016, 284, 1309, 616, 41803, 393, 6621, 467, 14720, 11, 645, 2300, 644, 318, 1016, 319, 4306, 11, 523, 314, 910, 314, 1183, 307, 625, 379, 642, 13, 314, 1392, 572, 670, 1903, 290, 651, 612, 379, 362, 25, 2231, 13, 314, 1282, 287, 1262, 616, 13952, 1994, 11, 2513, 287, 11, 766, 399, 8535, 2712, 351, 36062, 287, 262, 5228, 11, 25737, 3804, 503, 319, 262, 18507, 11, 290, 16914, 319, 262, 6891, 3084, 13, 8989, 2406, 422, 257, 1641, 47655, 351, 13230, 11, 314, 760, 644, 16914, 3073, 588, 13, 314, 836, 470, 760, 703, 881, 340, 373, 11, 475, 314, 714, 423, 23529, 276, 340, 510, 290, 5901, 616, 18057, 351, 340, 13, 314, 6810, 19772, 2024, 8347, 287, 262, 2166, 2119, 290, 399, 8535, 373, 287, 3294, 11685, 286, 8242, 290, 607, 7374, 15224, 13, 383, 4894, 373, 572, 13, 383, 2156, 373, 3863, 2319, 37, 532, 340, 373, 1542, 2354, 13, 220, 198, 198, 40, 1718, 399, 8535, 284, 616, 1097, 11, 290, 1444, 16679, 329, 281, 22536, 355, 314, 373, 12008, 25737, 373, 14904, 2752, 13, 220, 314, 1422, 470, 765, 284, 10436, 290, 22601, 503, 399, 8535, 523, 314, 9658, 287, 262, 1097, 290, 1309, 607, 711, 319, 616, 3072, 1566, 262, 22536, 5284, 13, 3226, 1781, 1644, 290, 32084, 3751, 510, 355, 880, 13, 314, 4893, 262, 3074, 290, 780, 399, 8535, 338, 9955, 318, 503, 286, 3240, 1762, 11, 34020, 14, 44, 4146, 547, 1444, 13, 1649, 484, 5284, 484, 547, 5897, 290, 4692, 11, 1422, 470, 1107, 1561, 11, 1718, 399, 8535, 11, 290, 1297, 502, 284, 467, 1363, 13, 220, 198, 198, 2025, 1711, 1568, 314, 651, 1363, 290, 41668, 32682, 7893, 502, 644, 314, 1053, 1760, 13, 314, 4893, 2279, 284, 683, 290, 477, 339, 550, 373, 8993, 329, 502, 13, 18626, 262, 2104, 1641, 1541, 2993, 290, 547, 28674, 379, 502, 329, 644, 314, 550, 1760, 13, 18626, 314, 373, 366, 448, 286, 1627, 290, 8531, 1, 780, 314, 1444, 16679, 878, 4379, 611, 673, 373, 1682, 31245, 6, 278, 780, 340, 2900, 503, 673, 373, 655, 47583, 503, 422, 262, 16914, 13, 775, 8350, 329, 2250, 290, 314, 1364, 290, 3377, 262, 1755, 379, 616, 1266, 1545, 338, 2156, 290, 16896, 477, 1755, 13, 314, 3521, 470, 5412, 340, 477, 523, 314, 2900, 616, 3072, 572, 290, 3088, 284, 8960, 290, 655, 9480, 866, 13, 2011, 1266, 1545, 373, 510, 477, 1755, 351, 502, 11, 5149, 502, 314, 750, 2147, 2642, 11, 290, 314, 1101, 8788, 13, 220, 198, 198, 40, 1210, 616, 3072, 319, 290, 314, 550, 6135, 13399, 14, 37348, 1095, 13, 31515, 11, 34020, 11, 47551, 11, 41668, 32682, 11, 290, 511, 7083, 1641, 1866, 24630, 502, 13, 1119, 389, 2282, 314, 20484, 607, 1204, 11, 20484, 399, 8535, 338, 1204, 11, 925, 2279, 517, 8253, 621, 340, 2622, 284, 307, 11, 925, 340, 1171, 618, 340, 373, 257, 366, 17989, 14669, 1600, 290, 20484, 25737, 338, 8395, 286, 1683, 1972, 20750, 393, 1719, 10804, 286, 607, 1200, 757, 11, 4844, 286, 606, 1683, 765, 284, 766, 502, 757, 290, 314, 481, 1239, 766, 616, 41803, 757, 11, 290, 484, 765, 502, 284, 1414, 329, 25737, 338, 7356, 6314, 290, 20889, 502, 329, 262, 32084, 1339, 290, 7016, 12616, 13, 198, 198, 40, 716, 635, 783, 2060, 13, 1406, 319, 1353, 286, 6078, 616, 1266, 1545, 286, 838, 812, 357, 69, 666, 32682, 828, 314, 481, 4425, 616, 7962, 314, 550, 351, 683, 11, 644, 314, 3177, 616, 1641, 11, 290, 616, 399, 8535, 13, 198, 198, 40, 4988, 1254, 12361, 13, 314, 423, 12361, 9751, 284, 262, 966, 810, 314, 1101, 7960, 2130, 318, 1016, 284, 1282, 651, 366, 260, 18674, 1, 319, 502, 329, 644, 314, 750, 13, 314, 460, 470, 4483, 13, 314, 423, 2626, 767, 8059, 422, 340, 13, 314, 1101, 407, 11029, 329, 7510, 13, 314, 423, 11668, 739, 616, 2951, 13, 314, 1053, 550, 807, 50082, 12, 12545, 287, 734, 2745, 13, 1629, 717, 314, 2936, 523, 6563, 287, 616, 2551, 475, 355, 262, 1528, 467, 416, 314, 1101, 3612, 3863, 484, 547, 826, 290, 314, 815, 423, 10667, 319, 607, 878, 4585, 16679, 290, 852, 5306, 3019, 992, 13, 314, 836, 470, 1337, 546, 25737, 7471, 11, 475, 314, 750, 18344, 257, 642, 614, 1468, 1200, 1497, 422, 607, 3397, 290, 314, 1254, 12361, 546, 340, 13, 314, 760, 2130, 287, 262, 1641, 481, 1011, 607, 287, 11, 475, 340, 338, 1239, 588, 852, 351, 534, 3397, 13, 1375, 481, 1663, 510, 20315, 278, 502, 329, 340, 290, 477, 314, 1053, 1683, 1760, 318, 1842, 607, 355, 616, 898, 13, 220, 198, 198, 22367, 11, 317, 2043, 32, 30, 4222, 1037, 502, 13, 383, 14934, 318, 6600, 502, 6776, 13, 220, 198, 24361, 25, 1148, 428, 2642, 30, 198, 33706, 25, 3763]]




def test_completion_openai_prompt():
    try:
        print("\n text 003 test\n")
        response = text_completion(
            model="text-davinci-003", prompt="What's the weather in SF?"
        )
        print(response)
        response_str = response["choices"][0]["text"]
        # print(response.choices[0])
        #print(response.choices[0].text)
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
# test_completion_openai_prompt()

def test_completion_openai_engine_and_model():
    try:
        print("\n text 003 test\n")
        litellm.set_verbose=True
        response = text_completion(
            model="text-davinci-003", engine="anything", prompt="What's the weather in SF?", max_tokens=5
        )
        print(response)
        response_str = response["choices"][0]["text"]
        # print(response.choices[0])
        #print(response.choices[0].text)
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
# test_completion_openai_engine_and_model()

def test_completion_openai_engine():
    try:
        print("\n text 003 test\n")
        litellm.set_verbose=True
        response = text_completion(
            engine="text-davinci-003", prompt="What's the weather in SF?", max_tokens=5
        )
        print(response)
        response_str = response["choices"][0]["text"]
        # print(response.choices[0])
        #print(response.choices[0].text)
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
# test_completion_openai_engine()


def test_completion_chatgpt_prompt():
    try:
        print("\n gpt3.5 test\n")
        response = text_completion(
            model="gpt-3.5-turbo", prompt="What's the weather in SF?"
        )
        print(response)
        response_str = response["choices"][0]["text"]
        print("\n", response.choices)
        print("\n", response.choices[0])
        #print(response.choices[0].text)
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
# test_completion_chatgpt_prompt()


def test_text_completion_basic():
    try:
        print("\n test 003 with echo and logprobs \n")
        litellm.set_verbose=False
        response = text_completion(
            model="text-davinci-003", prompt="good morning", max_tokens=10, logprobs=10, echo=True
        )
        print(response)
        print(response.choices)
        print(response.choices[0])
        #print(response.choices[0].text)
        response_str = response["choices"][0]["text"]
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
# test_text_completion_basic()


def test_completion_text_003_prompt_array():
    try:
        litellm.set_verbose=False
        response = text_completion(
            model="text-davinci-003", 
            prompt=token_prompt, # token prompt is a 2d list
        )
        print("\n\n response")

        print(response)
        # response_str = response["choices"][0]["text"]
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
# test_completion_text_003_prompt_array()


# not including this in our ci cd pipeline, since we don't want to fail tests due to an unstable replit
# def test_text_completion_with_proxy():
#     try:
#         litellm.set_verbose=True
#         response = text_completion(
#             model="facebook/opt-125m",
#             prompt='Write a tagline for a traditional bavarian tavern',
#             api_base="https://openai-proxy.berriai.repl.co/v1",
#             custom_llm_provider="openai",
#             temperature=0,
#             max_tokens=10,
#         )
#         print("\n\n response")

#         print(response)
#     except Exception as e:
#         pytest.fail(f"Error occurred: {e}")
# test_text_completion_with_proxy()

##### hugging face tests
def test_completion_hf_prompt_array():
    try:
        litellm.set_verbose=True
        print("\n testing hf mistral\n")
        response = text_completion(
            model="huggingface/mistralai/Mistral-7B-v0.1", 
            prompt=token_prompt, # token prompt is a 2d list,
            max_tokens=0,
            temperature=0.0,
            echo=True,
        )
        print("\n\n response")

        print(response)
        print(response.choices)
        assert(len(response.choices)==2)
        # response_str = response["choices"][0]["text"]
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")
# test_completion_hf_prompt_array()

def test_text_completion_stream():
    response = text_completion(
            model="huggingface/mistralai/Mistral-7B-v0.1", 
            prompt="good morning",
            stream=True
        )
    for chunk in response:
        print(chunk)
test_text_completion_stream()
