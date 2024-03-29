import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import math, copy, time
from torch.autograd import Variable

import matplotlib.pyplot as plt
import seaborn
seaborn.set_context(context='talk')
%matplotlib inline

# Architecture
class EncoderDecoder(nn.Module):
	"""
	A standard Encoder-Decoder architecture. Base for this and many
	other models
	"""
	def __init__(self, encoder, decoder, src_embed, tgt_embed, generator):
		super(EncoderDecoder, self).__init__()
		self.encoder = encoder
		self.decoder = decoder
		self.src_embed = src_embed
		self.tgt_embed = tgt_embed
		self.generator = generator

	def forward(self, src, tgt, src_mask, tgt_mask):
		# take in and process masked src and tgt sequences
		return self.decode(self.encode(src, src_mask), src_mask,
										tgt, tgt_mask)

	def encode(self, src, src_mask):
		return self.encoder(self.src_embed(src), src_mask)

	def decode(self, memory, src_mask, tgt, tgt_mask):
		return self.decoder(self.tgt_embed(tgt), memory, src_mask, tgt_mask)

class Generator(nn.Module):
	# define standard linear and softmax generation step
	def __init__(self, d_model, vocab):
		super(Generator, self).__init__()
		self.proj = nn.Linear(d_model, vocab)

# Encoder and Decoder stacks
# Encoder
def clones(module, N):
	# Produce N identical layers
	return nn.ModuleList([copy.deepcopy(module) for _ in range(N)])

class Encoder(nn.Module):
	# Core encoder is a stack of N layers
	def __init__(self, layer, N):
		super(Encoder, self).__init__()
		self.layers = clones(layer, N)
		self.norm = LayerNorm(layer.size)

	def forward(self, x, mask):
		# pass input (and mask) through each layer in turn
		for layer in self.layers:
			x = layer(x, mask)

		return self.norm(x)

class LayerNorm(nn.Module):
	# Construct a layernorm module
	def __init__(self, features, eps=1e-6):
		super(LayerNorm, self).__init__()
		self.a_2 = nn.Parameter(torch.ones(features))
		self.b_2 = nn.Parameter(torch.zeros(features))
		self.eps = eps

	def forward(self, x):
		mean = x.mean(-1, keepdim=True)
		std = x.std(-1, keepdim=True)
		return self.a_2 * (x - mean) / (std + self.eps) + self.b_2

class SublayerConnection(nn.Module):
	"""
	A residual connection followed by a layer norm
	Note for code simplicity the norm is first as opposed to last
	"""
	def __init__(self, size, dropout):
		super(SublayerConnection, self).__init__()
		self.norm = LayerNorm(size)
		self.dropout = nn.Dropout(dropout)

	def forward(self, x, sublayer):
		# Apply residual connection to any sublayer with the same size
		return x + self.dropout(sublayer(self.norm(x)))

class EncoderLayer(nn.Module):
	# Encoder is made up of self attention and feed forward
	def __init__(self, size, self_attn, feed_forward, dropout):
		super(EncoderLayer, self).__init()__
		self.self_attn = self_attn
		self.feed_forward = feed_forward
		self.sublayer = clones(SublayerConnection(size, dropout), 2)
		self.size = size

	def forward(self, x, mask):
		x = self.sublayer[0](x, lambda x:self.self_attn(x, x, x, mask))
		return self.sublayer[1](x, self.feed_forward)