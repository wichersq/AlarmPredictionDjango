import tensorflow as tf

def dumb_model(x):
  """Gets about 3500 error"""
  pred = x[:,0]
  add = tf.Variable(0.0)
  pred += add
  return pred

def NN_model(x):
  pred = tf.layers.dense(inputs = x, units = 100, activation = tf.nn.leaky_relu)
  pred = tf.layers.dense(inputs = pred, units = 50, activation = tf.nn.leaky_relu)
  pred = tf.layers.dense(inputs = pred, units = 10, activation = tf.nn.leaky_relu) 
  pred = tf.layers.dense(inputs = pred, units = 5, activation = tf.nn.leaky_relu)
  pred = tf.layers.dense(inputs =pred, units = 1)
  return pred

tf.reset_default_graph()

list_samp_x = ['Driving_Duration', 'Price Level','Does_Price_Lv_Exist?', 'Rating', 'Does_Rating_Exist?', 'Reviews', 'Does_Reviews_Exist?', 'Importance']
x = tf.placeholder(shape=(None, len(list_samp_x)), dtype=tf.float32)
y_ = tf.placeholder(shape=(None, 1), dtype=tf.float32)
pred = NN_model(x)

loss = tf.square(y_ - pred)
error = tf.abs(y_ - pred)
loss = tf.reduce_mean(loss)
error = tf.reduce_mean(error)

opt = tf.train.AdamOptimizer(.0003).minimize(loss)

saver = tf.train.Saver()

sess =tf.Session()
sess.run(tf.global_variables_initializer())

path = "./model_checkpoint/"

def train_iter(samp_x, samp_y):
    _, loss_val, error_val = sess.run([opt, loss, error], feed_dict={x:samp_x, y_:samp_y})
    return loss_val, error_val

def get_error(samp_x, samp_y):
    loss_val, error_val = sess.run([loss, error], feed_dict={x:samp_x, y_:samp_y})
    return loss_val, error_val

def inference(samp_x):
    return sess.run(pred, feed_dict={x:samp_x})


def save(global_step):
    saver.save(sess, path, global_step=global_step)

def restore():
    saver.restore(sess, tf.train.latest_checkpoint(path))



