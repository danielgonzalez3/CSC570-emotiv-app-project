from cortex import Cortex
import multiprocessing
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3

def add_point(points, colors, fig, point: [float, float, float]):
    # global points, colors
    points.append(point)
    colors.append([1, 0, 0, 1.0])  # default color is red
    update(points, colors, len(points)-1, fig)

def update(points, colors, num, fig):
    ax = p3.Axes3D(fig)
    ax.clear()  # Clear the plot

    # Set the limits of the x, y, and z axes
    # ax.set_xlim(x_scale)
    # ax.set_ylim(y_scale)
    # ax.set_zlim(z_scale)

    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    ax.set_zlim([-3, 3])

    points_to_pop = []
    for i in range(len(colors)):
        colors[i][3] -= 0.05
        if colors[i][3] <= 0:
            points_to_pop.append(i)

    # Remove all the points that have faded away.
    for i in sorted(points_to_pop, reverse=True):  # We pop the indices from highest to lowest.
        points.pop(i)
        colors.pop(i)

    for point, color in zip(points, colors):
        # ax.scatter(data[0, i:i+1], data[1, i:i+1], data[2, i:i+1], color=colors[i])
        ax.scatter(*point, color=color)
    text = ax.text2D(0.05, 0.95, f'Iteration: {num+1}', transform=ax.transAxes)

def run_animation(points, colors, queue):
    # ani = animation.FuncAnimation(fig, update_and_add_point, frames=100, interval=50)
    fig = plt.figure()
    # ax = p3.Axes3D(fig)

    # Initialize a text object
    # text = ax.text2D(0.05, 0.95, '', transform=ax.transAxes)
    plt.ion()
    plt.show()
    while True:
        if not queue.empty():
            fused_vector = queue.get()
            print(fused_vector)
            add_point(points, colors, fig, fused_vector)
        plt.draw()
        plt.pause(0.01)

        if not plt.get_fignums():
            break

def get_pad_vector(data):
    labels = ['eng.isActive', 'Engagement', 'exc.isActive', 'Excitement', 'Long term excitement. ', 'str.isActive', 'Stress ', 'rel.isActive', 'Relaxation', 'int.isActive', 'Interest ', 'foc.isActive', 'Focus']
    pad_mapping = {
        'Engagement': [1, 1, 1],
        'Excitement': [1, 1, -1],
        'Stress ': [-1, 1, -1],
        'Relaxation': [1, -1, 1],
        'Interest ': [1, 1, -1],
        'Focus': [1, -1, 1]
    }
    for i in range(len(data['met'])):
        key = list(labels)[i]
        value = data['met'][i]
        if key in pad_mapping:
            pad_values = pad_mapping[key]
            multiplied_values = [v * value for v in pad_values]
            pad_mapping[key] = multiplied_values
    fused_vector = [0, 0, 0]
    for vector in pad_mapping.values():
        fused_vector = [x + y for x, y in zip(fused_vector, vector)]
    return fused_vector

class Subcribe():
    """
    A class to subscribe data stream.

    Attributes
    ----------
    c : Cortex
        Cortex communicate with Emotiv Cortex Service

    Methods
    -------
    start():
        start data subscribing process.
    sub(streams):
        To subscribe to one or more data streams.
    on_new_data_labels(*args, **kwargs):
        To handle data labels of subscribed data
    on_new_eeg_data(*args, **kwargs):
        To handle eeg data emitted from Cortex
    on_new_mot_data(*args, **kwargs):
        To handle motion data emitted from Cortex
    on_new_dev_data(*args, **kwargs):
        To handle device information data emitted from Cortex
    on_new_met_data(*args, **kwargs):
        To handle performance metrics data emitted from Cortex
    on_new_pow_data(*args, **kwargs):
        To handle band power data emitted from Cortex
    """
    def __init__(self, app_client_id, app_client_secret, queue=None, **kwargs):
        """
        Constructs cortex client and bind a function to handle subscribed data streams
        If you do not want to log request and response message , set debug_mode = False. The default is True
        """
        print("Subscribe __init__")
        self.queue = queue
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(new_data_labels=self.on_new_data_labels)
        self.c.bind(new_eeg_data=self.on_new_eeg_data)
        self.c.bind(new_mot_data=self.on_new_mot_data)
        self.c.bind(new_dev_data=self.on_new_dev_data)
        self.c.bind(new_met_data=self.on_new_met_data)
        self.c.bind(new_pow_data=self.on_new_pow_data)
        self.c.bind(new_fe_data=self.on_new_fe_data)
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, streams, headsetId=''):
        """
        To start data subscribing process as below workflow
        (1)check access right -> authorize -> connect headset->create session
        (2) subscribe streams data
        'eeg': EEG
        'mot' : Motion
        'dev' : Device information
        'met' : Performance metric
        'pow' : Band power
        'eq' : EEQ Quality

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot']
        headsetId: string , optional
             id of wanted headet which you want to work with it.
             If the headsetId is empty, the first headset in list will be set as wanted headset
        Returns
        -------
        None
        """
        self.streams = streams

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def sub(self, streams):
        """
        To subscribe to one or more data streams
        'eeg': EEG
        'mot' : Motion
        'dev' : Device information
        'met' : Performance metric
        'pow' : Band power

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot']

        Returns
        -------
        None
        """
        self.c.sub_request(streams)

    def unsub(self, streams):
        """
        To unsubscribe to one or more data streams
        'eeg': EEG
        'mot' : Motion
        'dev' : Device information
        'met' : Performance metric
        'pow' : Band power

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot']

        Returns
        -------
        None
        """
        self.c.unsub_request(streams)

    def on_new_data_labels(self, *args, **kwargs):
        """
        To handle data labels of subscribed data
        Returns
        -------
        data: list
              array of data labels
        name: stream name
        For example:
            eeg: ["COUNTER","INTERPOLATED", "AF3", "T7", "Pz", "T8", "AF4", "RAW_CQ", "MARKER_HARDWARE"]
            motion: ['COUNTER_MEMS', 'INTERPOLATED_MEMS', 'Q0', 'Q1', 'Q2', 'Q3', 'ACCX', 'ACCY', 'ACCZ', 'MAGX', 'MAGY', 'MAGZ']
            dev: ['AF3', 'T7', 'Pz', 'T8', 'AF4', 'OVERALL']
            met : ['eng.isActive', 'eng', 'exc.isActive', 'exc', 'lex', 'str.isActive', 'str', 'rel.isActive', 'rel', 'int.isActive', 'int', 'foc.isActive', 'foc']
            pow: ['AF3/theta', 'AF3/alpha', 'AF3/betaL', 'AF3/betaH', 'AF3/gamma', 'T7/theta', 'T7/alpha', 'T7/betaL', 'T7/betaH', 'T7/gamma', 'Pz/theta', 'Pz/alpha', 'Pz/betaL', 'Pz/betaH', 'Pz/gamma', 'T8/theta', 'T8/alpha', 'T8/betaL', 'T8/betaH', 'T8/gamma', 'AF4/theta', 'AF4/alpha', 'AF4/betaL', 'AF4/betaH', 'AF4/gamma']
        """
        data = kwargs.get('data')
        stream_name = data['streamName']
        stream_labels = data['labels']
        print('{} labels are : {}'.format(stream_name, stream_labels))

    def on_new_eeg_data(self, *args, **kwargs):
        """
        To handle eeg data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array eeg match the labels in the array labels return at on_new_data_labels
        For example:
           {'eeg': [99, 0, 4291.795, 4371.795, 4078.461, 4036.41, 4231.795, 0.0, 0], 'time': 1627457774.5166}
        """
        data = kwargs.get('data')
        # print('eeg data: {}'.format(data))

    def on_new_mot_data(self, *args, **kwargs):
        """
        To handle motion data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array motion match the labels in the array labels return at on_new_data_labels
        For example: {'mot': [33, 0, 0.493859, 0.40625, 0.46875, -0.609375, 0.968765, 0.187503, -0.250004, -76.563667, -19.584995, 38.281834], 'time': 1627457508.2588}
        """
        data = kwargs.get('data')
        # print('motion data: {}'.format(data))

    def on_new_dev_data(self, *args, **kwargs):
        """
        To handle dev data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array dev match the labels in the array labels return at on_new_data_labels
        For example:  {'signal': 1.0, 'dev': [4, 4, 4, 4, 4, 100], 'batteryPercent': 80, 'time': 1627459265.4463}
        """
        data = kwargs.get('data')
        # print('dev data: {}'.format(data))

    def on_new_met_data(self, *args, **kwargs):
        """
        To handle performance metrics data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array met match the labels in the array labels return at on_new_data_labels
        For example: {'met': [True, 0.5, True, 0.5, 0.0, True, 0.5, True, 0.5, True, 0.5, True, 0.5], 'time': 1627459390.4229}
        """
        data = kwargs.get('data')


        print('pm data: {}'.format(data))
        fused_vector = get_pad_vector(data)
        if self.queue:
            self.queue.put(fused_vector)

    def on_new_pow_data(self, *args, **kwargs):
        """
        To handle band power data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array pow match the labels in the array labels return at on_new_data_labels
        For example: {'pow': [5.251, 4.691, 3.195, 1.193, 0.282, 0.636, 0.929, 0.833, 0.347, 0.337, 7.863, 3.122, 2.243, 0.787, 0.496, 5.723, 2.87, 3.099, 0.91, 0.516, 5.783, 4.818, 2.393, 1.278, 0.213], 'time': 1627459390.1729}
        """
        data = kwargs.get('data')
        # print('pow data: {}'.format(data))

    def on_new_fe_data(self, *args, **kwargs):
        data = kwargs.get('data')
        # print('fe data: {}'.format(data))

    # callbacks functions
    def on_create_session_done(self, *args, **kwargs):
        print('on_create_session_done')

        # subribe data
        self.sub(self.streams)

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        print(error_data)




# -----------------------------------------------------------
#
# GETTING STARTED
#   - Please reference to https://emotiv.gitbook.io/cortex-api/ first.
#   - Connect your headset with dongle or bluetooth. You can see the headset via Emotiv Launcher
#   - Please make sure the your_app_client_id and your_app_client_secret are set before starting running.
#   - In the case you borrow license from others, you need to add license = "xxx-yyy-zzz" as init parameter
# RESULT
#   - the data labels will be retrieved at on_new_data_labels
#   - the data will be retreived at on_new_[dataStream]_data
#
# -----------------------------------------------------------

def main(queue):

    # Please fill your application clientId and clientSecret before running script
    # your_app_client_id = 'RMrZA8LTi5mdlFhwyy5iVL38pJm2Tua215X0Kc8R'
    # your_app_client_secret = 'BWXdNry3tf3lVAYVhkLvIURD5BIz8DDEHfZAQHsPweisUiiRolSj6gjdCcUKgvLuBcB91qm5JwE5d6gaoo0lKrkMuNJ4UmiCQ7n0BfLL15eUfqF2M1io178KDZ5Sf1UQ'

    # this one has eeg but no license
    # your_app_client_id = 'l5C1FOIYJbBBLgNYG3OfehADxE0rlJA8NtlHfz8c'
    # your_app_client_secret = 'Sdn5Ggo4wEyyTuD9RTh4p6NlVM92erq2TiAf0LkrYmWdhnx7dOZupbM7cjTQl0ZpaYK4NT0WpggeIuGFHjpwtBBmyjJeQWFYdoolsVsGgYpL14GjmNnJTLXhkhMI6Py5'

    # this one does not have eeg
    your_app_client_id = 'Awu9Nd8x6SIkxQOkgtmBvtbeOk6YsMxaviim8xRZ'
    your_app_client_secret = 'ON14cHcIKhYLPx7rwWlPCfdnom70MPZ4C4DQJ2qHfiVWTd3FZog8bT1bKOkri5AH6ZtpnGVKSp2YM7cBodTiI829N3gqAUVPGNVr11o9Bp73vbC3lZ7lSkb6ch8U0gIB'

    s = Subcribe(your_app_client_id, your_app_client_secret, queue=queue)

    # list data streams
    streams = ['eeg','mot','met','pow', 'dev', 'met', 'fac']
    s.start(streams)

if __name__ =='__main__':
    queue = multiprocessing.Queue()
    # vectors = []
    points = []
    colors = []

    # fig = plt.figure()
    receiver = multiprocessing.Process(target=run_animation, args=(points, colors, queue, ))
    receiver.start()

    sender = multiprocessing.Process(target=main, args=(queue,))
    sender.start()
    # main()

# -----------------------------------------------------------
