from flask.signals import _signals

# 机器人
ROBOT_START = _signals.signal('ROBOT_START')
ROBOT_STOP = _signals.signal('ROBOT_STOP')

# 盒子
DEVICE_CONNECTED = _signals.signal('DEVICE_CONNECTED')
DEVICE_ERROR = _signals.signal('DEVICE_ERROR')

# 产品
PRODUCT_BEGIN = _signals.signal('PRODUCT_BEGIN')
PRODUCT_FINISHED = _signals.signal('PRODUCT_FINISHED')
