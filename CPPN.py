import tensorflow as tf
import numpy as np
import Helpers as hp
import math


image_name = 'test/test'

# Model parameters
x_dim = 2560
y_dim = 1440
z_dim = 1
scale = 10.0
num_layers = 9
layer_size = 17
stddev = 1.0
rgb = False
activation = tf.nn.tanh


def construct_input(x_dim, y_dim, z_dim, scale):
    x = []
    y = []
    r = []
    for _x in range(x_dim):
        x_coord = (_x / (x_dim - 1) - 0.5) * 2 * scale
        for _y in range(y_dim):
            y_coord = (_y / (y_dim - 1) - 0.5) * 2 * scale
            r_coord = math.sqrt(x_coord ** 2 + y_coord ** 2)
            x.append(x_coord)
            y.append(y_coord)
            r.append(r_coord)
    x = tf.constant(x, name='x')
    y = tf.constant(y, name='y')
    r = tf.constant(r, name='r')
    coords = tf.stack([x, y, r], axis=1, name='coords')

    z = np.random.uniform(-1.0, 1.0, size=(z_dim)).astype(np.float32) * scale
    z = np.reshape(np.tile(z, x_dim * y_dim), (x_dim * y_dim, z_dim))
    z = tf.constant(z, name='z')

    inputs = tf.concat([z, coords], 1)
    return inputs

inputs = construct_input(x_dim, y_dim, z_dim, scale)

# Construct model
cppn = hp.fully_connected(inputs, layer_size, name='layer_0',
                          bias=False, stddev=stddev, activation=tf.nn.tanh)
for i in range(num_layers):
    cppn = hp.fully_connected(cppn, layer_size, name='layer_'+str(i+1),
                              stddev=stddev, activation=activation)
channels = 3 if rgb else 1
cppn = hp.fully_connected(cppn, channels, name='output',
                          stddev=stddev, activation=tf.nn.sigmoid)
if rgb:
    cppn = tf.reshape(cppn, [x_dim, y_dim, 3])
else:
    cppn = tf.reshape(cppn, [x_dim, y_dim])

# Run model
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    im = sess.run(cppn)

# Save the image
hp.save_image(im, image_name)

