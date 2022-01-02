{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "GlK6GW-xK88A"
   },
   "source": [
    "# **Thinking in tensors, writing in PyTorch**\n",
    "Hands-on course by [Piotr Migdał](https://p.migdal.pl). This notebook prepared by [Weronika Ormaniec](https://github.com/werkaaa). Version for ML in PL 2019 workshop.\n",
    "\n",
    "## ConvNets: Convolutions\n",
    "\n",
    "<a href=\"https://colab.research.google.com/github/stared/thinking-in-tensors-writing-in-pytorch/blob/master/convnets/Convolutions.ipynb\" target=\"_parent\">\n",
    "    <img src=\"https://colab.research.google.com/assets/colab-badge.svg\"/>\n",
    "</a>\n",
    "\n",
    "![](https://github.com/vdumoulin/conv_arithmetic/blob/master/gif/same_padding_no_strides.gif?raw=true)\n",
    "\n",
    "(image source: [Convolution arithmetic](https://github.com/vdumoulin/conv_arithmetic))\n",
    "\n",
    "Convolution (properly cross-correlation) is an operation on kernel and input data. It consists of following steps:\n",
    "* Place the kernel above the input data\n",
    "* Perform an elementwise multiplication between kernel elements and overlaping input elements and sum the products\n",
    "* Repeat for all pixels of the input data\n",
    "\n",
    "Each convolution layer produces new channels based on those which preceded it. First, we start with 3 channels for red, green and blue (RGB) components. Next, channels get more and more abstract.\n",
    "\n",
    "While producing new channels with representations of various properties of the image, we also reduce the resolution, usually using pooling layers.\n",
    "\n",
    "See also:\n",
    "* [Image Kernels - visually explained](http://setosa.io/ev/image-kernels/)\n",
    "* [How neural networks build up their understanding of images](https://distill.pub/2017/feature-visualization/) by Chris Olah et al at Distill\n",
    "* [Convolutional Neural Networks by Andrej Karpathy](http://cs231n.github.io/convolutional-networks/) for in-depth explanation of convolutions and other accompanying blocks\n",
    "* [CNNs, Part 1: An Introduction to Convolutional Neural Networks](https://victorzhou.com/blog/intro-to-cnns-part-1/) by Victor Zhou\n",
    "* [How do Convolutional Neural Networks work?](http://brohrer.github.io/how_convolutional_neural_networks_work.html)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Downgrading matplotlib, so seaborn works correctly. Use only in Colab.\n",
    "!pip install matplotlib==3.1.0 --quiet"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 147
    },
    "colab_type": "code",
    "id": "nbAxaziqsXao",
    "outputId": "24d446a4-7fb3-44f8-ffc2-deccb4e72079"
   },
   "outputs": [],
   "source": [
    "import torch\n",
    "from torch import utils\n",
    "from torchvision import transforms\n",
    "import torchvision\n",
    "from PIL import Image\n",
    "import requests\n",
    "from io import BytesIO\n",
    "import torch.nn.functional as F\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "aRSdW_kWRhoQ"
   },
   "source": [
    "## Tic-tac-toe"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "R_epEqwgFjvZ"
   },
   "source": [
    "Firstly, we will play with an one-channel tic-tac-toe board. Let's look at 6 kernels which will try to detect 6 particular patterns at the tic-tac-toe bord. "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "Rhl8Qf5FbG0m"
   },
   "outputs": [],
   "source": [
    "class Tic_tac_toe():\n",
    "\n",
    "    def __init__(self, width, height):\n",
    "        self.width = width\n",
    "        self.height = height\n",
    "        self.board = torch.zeros(4*width+3, 4*height+3)\n",
    "\n",
    "    def place_X(self, x, y):\n",
    "        x_pos = 4*x + 3\n",
    "        y_pos = 4*y + 3\n",
    "        dx = [-1, 1, 1, -1]\n",
    "        dy = [-1, 1, -1, 1]\n",
    "        for i, j in zip(dx, dy):\n",
    "            self.board[y_pos+i][x_pos+j] = 1.0\n",
    "        self.board[y_pos][x_pos] = 1.0\n",
    "\n",
    "    def place_O(self, x, y):\n",
    "        x_pos = 4*x + 3\n",
    "        y_pos = 4*y + 3\n",
    "        dx = [-1, 1, 0, 0]\n",
    "        dy = [0, 0, -1, 1]\n",
    "        for i, j in zip(dx, dy):\n",
    "            self.board[y_pos+i][x_pos+j] = 1.0\n",
    "\n",
    "    def fill_up(self, X, O):\n",
    "        for (x, y) in X:\n",
    "            self.place_X(x, y)\n",
    "\n",
    "        for (x, y) in O:\n",
    "            self.place_O(x, y)\n",
    "\n",
    "    def __str__(self):\n",
    "        return str(self.board)\n",
    "\n",
    "    def draw(self):\n",
    "        plt.imshow(self.board, cmap=\"gray\")\n",
    "        plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "WWfKPTcXsqj-"
   },
   "source": [
    "Create a tic-tac-toe board of preferred size and place marks on it."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "cellView": "form",
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 265
    },
    "colab_type": "code",
    "id": "ziD6_IYlQHEb",
    "outputId": "897f5f51-730a-45e0-9204-20fef46275f0"
   },
   "outputs": [],
   "source": [
    "#@title Create a tic-tac-toe board\n",
    "width = 5  # @param {type:\"integer\"}\n",
    "height = 5  # @param {type:\"integer\"}\n",
    "place_X = [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4)]  # @param {}\n",
    "place_O = [(0, 0), (0, 1), (1, 0), (2, 1), (3, 2), (4, 3)]  # @param {}\n",
    "\n",
    "tic_tac_toe = Tic_tac_toe(5, 5)\n",
    "tic_tac_toe.fill_up(X=place_X, O=place_O)\n",
    "board = tic_tac_toe.board\n",
    "tic_tac_toe.draw()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "_b6K4DNnLC4F"
   },
   "outputs": [],
   "source": [
    "def visualize_kernels(kernels, s=3, annot=True, l=0):\n",
    "    columns = len(kernels)\n",
    "    fig, axs = plt.subplots(1, columns, figsize=(s*columns, s))\n",
    "    j = 0\n",
    "    for k in kernels.keys():\n",
    "        ax = axs[j]\n",
    "        ax.set_title(k)\n",
    "        sns.heatmap(kernels[k].squeeze(dim=0).squeeze(\n",
    "            dim=0), ax=ax, annot=annot, cbar=False, linewidths=l, cmap=\"YlGnBu\", fmt=\".1f\")\n",
    "        ax.axis('off')\n",
    "        j = j+1"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "pgFqnbGst-ET"
   },
   "source": [
    "Now, let's look at 2 kernels, which will help us with the analisis of the board."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 210
    },
    "colab_type": "code",
    "id": "oCFa57cn0TBx",
    "outputId": "5d0df772-3690-49a1-b2e0-d213bda89e37"
   },
   "outputs": [],
   "source": [
    "x_o_kernels = {\n",
    "    'x': torch.tensor([[[[1.0, 0.0, 1.0],\n",
    "                         [0.0, 1.0, 0.0],\n",
    "                         [1.0, 0.0, 1.0]]]]),\n",
    "    'o': torch.tensor([[[[0.0, 1.0, 0.0],\n",
    "                         [1.0, 0.0, 1.0],\n",
    "                         [0.0, 1.0, 0.0]]]])\n",
    "}\n",
    "visualize_kernels(x_o_kernels, l=.5)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "H-9B2478ulOo"
   },
   "source": [
    "Firstly, we apply the **x** kernel and **o** kernel to the input image respectively. As you can see, places where crosses and circles were located have now the biggest values."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "cellView": "form",
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 591
    },
    "colab_type": "code",
    "id": "wJXIR4vKYCZw",
    "outputId": "29f9d80e-9862-4622-dcdb-152670bf1201"
   },
   "outputs": [],
   "source": [
    "#@title Specify bias and activation function:\n",
    "bias = 0  # @param {type:\"slider\", min:-5, max:5, step:0.5}\n",
    "activation_function = \"Identity\"  # @param [\"Identity\", \"ReLU\", \"Sigmoid\"]\n",
    "\n",
    "functions = {'Identity': lambda x: x,\n",
    "             'ReLU': torch.relu,\n",
    "             'Sigmoid': torch.sigmoid}\n",
    "activation = functions[activation_function]\n",
    "\n",
    "layer1 = {k+' kernel': activation(torch.conv2d(board.unsqueeze(dim=0).unsqueeze(dim=0), v)+bias)\n",
    "          for (k, v) in x_o_kernels.items()}\n",
    "visualize_kernels(layer1, s=10)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "Aa2naWWl9byA"
   },
   "source": [
    "Try changing the bias value, so places where crosses and circles were located are more visible. You can also add the activation function."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "5Co0I2b7wEUs"
   },
   "source": [
    "To make it even more clear, let's apply max pooling operation. Out of every four pixels we will choose one with the greatest value.\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "cellView": "form",
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 373
    },
    "colab_type": "code",
    "id": "cjQrxWDzZ4w7",
    "outputId": "579565c5-ab78-4bbf-f86b-cc1000a94785"
   },
   "outputs": [],
   "source": [
    "#@title Specify pooling:\n",
    "pooling_kernel_size = 2  # @param {type:\"number\"}\n",
    "pooling_type = \"max-pooling\"  # @param [\"max-pooling\", \"avg-pooling\"]\n",
    "types = {'avg-pooling': F.avg_pool2d, 'max-pooling': F.max_pool2d}\n",
    "pooling = types[pooling_type]\n",
    "layer1_pooling = {k+'+'+pooling_type: pooling(v, pooling_kernel_size)\n",
    "                  for (k, v) in layer1.items()}\n",
    "visualize_kernels(layer1_pooling, s=6)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "X9jwCpZUyQhd"
   },
   "source": [
    "Sometimes, we don't have to use max pooling of size 2 here. You can try to use average pooling here  or choose a different size of the kernel."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "G5tVUmnI2572"
   },
   "source": [
    "Finally, we can use 4 more kernels to find lines of croses and circles."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 210
    },
    "colab_type": "code",
    "id": "ocwcmwEXOExe",
    "outputId": "4bc4b488-f7c7-4028-da5e-34f42073c17b"
   },
   "outputs": [],
   "source": [
    "line_kernels = {\n",
    "    'vertical': torch.tensor([[[[0.0, 1.0, 0.0],\n",
    "                                [0.0, 1.0, 0.0],\n",
    "                                [0.0, 1.0, 0.0]]]]),\n",
    "    'horizontal': torch.tensor([[[[0.0, 0.0, 0.0],\n",
    "                                  [1.0, 1.0, 1.0],\n",
    "                                  [0.0, 0.0, 0.0]]]]),\n",
    "    'diagonal_1': torch.tensor([[[[0.0, 0.0, 1.0],\n",
    "                                  [0.0, 1.0, 0.0],\n",
    "                                  [1.0, 0.0, 0.0]]]]),\n",
    "    'diagonal_2': torch.tensor([[[[1.0, 0.0, 0.0],\n",
    "                                  [0.0, 1.0, 0.0],\n",
    "                                  [0.0, 0.0, 1.0]]]])\n",
    "\n",
    "}\n",
    "visualize_kernels(line_kernels, l=.5)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "kXw1fpGqRD-8"
   },
   "source": [
    "Let's use remaining kernels combined with max pooling and ReLU to see, where whole lines of crosses and circles were located."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 512
    },
    "colab_type": "code",
    "id": "qNBGTaCZ2R2q",
    "outputId": "60a85b0e-b5f1-4752-8bf8-08e4c289e837"
   },
   "outputs": [],
   "source": [
    "layer1_ = list(layer1_pooling.values())\n",
    "layer2_x = {k+' x': torch.conv2d(layer1_[0], v)\n",
    "            for (k, v) in line_kernels.items()}\n",
    "layer2_o = {k+' o': torch.conv2d(layer1_[1], v)\n",
    "            for (k, v) in line_kernels.items()}\n",
    "visualize_kernels(layer2_x, s=4)\n",
    "visualize_kernels(layer2_o, s=4)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "cellView": "form",
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 512
    },
    "colab_type": "code",
    "id": "2G5P9UkZzRYo",
    "outputId": "05eddafd-c107-43ab-85bf-823b09560e3c"
   },
   "outputs": [],
   "source": [
    "# @title Specify second layer parameters:\n",
    "pooling_kernel_size = 2  # @param {type:\"number\"}\n",
    "pooling_type = \"max-pooling\"  # @param [\"max-pooling\", \"avg-pooling\"]\n",
    "types = {'avg-pooling': F.avg_pool2d, 'max-pooling': F.max_pool2d}\n",
    "pooling = types[pooling_type]\n",
    "bias = 0  # @param {type:\"slider\", min:-5, max:5, step:0.5}\n",
    "\n",
    "activation_function = \"Identity\"  # @param [\"Identity\", \"ReLU\", \"Sigmoid\"]\n",
    "functions = {'Identity': lambda x: x,\n",
    "             'ReLU': torch.relu,\n",
    "             'Sigmoid': torch.sigmoid}\n",
    "activation = functions[activation_function]\n",
    "\n",
    "layer2_x_activation = {k+'+activation': pooling(activation(\n",
    "    v+bias), pooling_kernel_size) for (k, v) in layer2_x.items()}\n",
    "layer2_o_activation = {k+'+activation': pooling(activation(\n",
    "    v+bias), pooling_kernel_size) for (k, v) in layer2_o.items()}\n",
    "visualize_kernels(layer2_x_activation, s=4)\n",
    "visualize_kernels(layer2_o_activation, s=4)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "colab_type": "text",
    "id": "whCON0Eo3hc7"
   },
   "source": [
    "## Bigger picture"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "On bigger scale, pattern recognition is nicely visible on edge detection by so called Sobel kernels."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "cellView": "form",
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 285
    },
    "colab_type": "code",
    "id": "4V6mTGNtSS9R",
    "outputId": "65375500-27b9-4e63-eb0d-752592ab64c5"
   },
   "outputs": [],
   "source": [
    "#@markdown ### Enter a path with the photo:\n",
    "#\"https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Common_zebra_1.jpg/250px-Common_zebra_1.jpg\"\n",
    "\n",
    "# @param {type:\"string\"}\n",
    "file_path = \"https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Common_zebra_1.jpg/250px-Common_zebra_1.jpg\"\n",
    "\n",
    "if \":\" in file_path:\n",
    "    response = requests.get(file_path)\n",
    "    img = Image.open(BytesIO(response.content))\n",
    "else:\n",
    "    img = Image.open(file_path)\n",
    "\n",
    "transform = transforms.Compose([\n",
    "    transforms.Resize((64, 64)),\n",
    "    transforms.Grayscale(),\n",
    "    transforms.ToTensor()])\n",
    "\n",
    "img_tensor = transform(img)\n",
    "plt.imshow(img_tensor.squeeze(dim=0), cmap=\"gray\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {},
    "colab_type": "code",
    "id": "ng0LoK2QWCIe"
   },
   "outputs": [],
   "source": [
    "sobel_vertical_kernel = torch.tensor([[[[-1.0, 0.0, 1.0],\n",
    "                                        [-2.0, 0.0, 2.0],\n",
    "                                        [-1.0, 0.0, 1.0]]]])\n",
    "\n",
    "sobel_horizontal_kernel = torch.tensor([[[[-1.0, -2.0, -1.0],\n",
    "                                          [0.0, 0.0, 0.0],\n",
    "                                          [1.0, 2.0, 1.0]]]])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 268
    },
    "colab_type": "code",
    "id": "d9yahXnUWwFq",
    "outputId": "49753f4d-2f66-48bf-c94a-5f48f4410e0d"
   },
   "outputs": [],
   "source": [
    "zebra_with_sobel_vertical = torch.conv2d(\n",
    "    img_tensor.unsqueeze(dim=0), sobel_vertical_kernel)\n",
    "plt.imshow(zebra_with_sobel_vertical.squeeze(\n",
    "    dim=0).squeeze(dim=0), cmap=\"gray\")\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/",
     "height": 268
    },
    "colab_type": "code",
    "id": "6UlzwvhqYg44",
    "outputId": "3300644c-83f8-4ff0-b349-a5b002fc9c4a"
   },
   "outputs": [],
   "source": [
    "zebra_with_sobel_horizontal = torch.conv2d(\n",
    "    img_tensor.unsqueeze(dim=0), sobel_horizontal_kernel)\n",
    "plt.imshow(zebra_with_sobel_horizontal.squeeze(\n",
    "    dim=0).squeeze(dim=0), cmap=\"gray\")\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "You can try and experiment with your own images."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "accelerator": "GPU",
  "colab": {
   "collapsed_sections": [
    "aRSdW_kWRhoQ",
    "whCON0Eo3hc7",
    "3zl3m7Yrccex"
   ],
   "name": "Convolutions.ipynb",
   "provenance": []
  },
  "kernelspec": {
   "display_name": "Python [conda env:py37]",
   "language": "python",
   "name": "conda-env-py37-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.2"
  },
  "toc": {
   "base_numbering": 1,
   "nav_menu": {},
   "number_sections": true,
   "sideBar": true,
   "skip_h1_title": false,
   "title_cell": "Table of Contents",
   "title_sidebar": "Contents",
   "toc_cell": false,
   "toc_position": {},
   "toc_section_display": true,
   "toc_window_display": false
  },
  "varInspector": {
   "cols": {
    "lenName": 16,
    "lenType": 16,
    "lenVar": 40
   },
   "kernels_config": {
    "python": {
     "delete_cmd_postfix": "",
     "delete_cmd_prefix": "del ",
     "library": "var_list.py",
     "varRefreshCmd": "print(var_dic_list())"
    },
    "r": {
     "delete_cmd_postfix": ") ",
     "delete_cmd_prefix": "rm(",
     "library": "var_list.r",
     "varRefreshCmd": "cat(var_dic_list()) "
    }
   },
   "types_to_exclude": [
    "module",
    "function",
    "builtin_function_or_method",
    "instance",
    "_Feature"
   ],
   "window_display": false
  }
 },
 "nbformat": 4,
 "nbformat_minor": 1
}
