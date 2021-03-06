import numpy as np


def make_reuters_data(data_dir):
    np.random.seed(1234)
    from sklearn.feature_extraction.text import CountVectorizer
    from os.path import join
    did_to_cat = {}
    cat_list = ['CCAT', 'GCAT', 'MCAT', 'ECAT']
    with open(join(data_dir, 'rcv1-v2.topics.qrels')) as fin:
        for line in fin.readlines():
            line = line.strip().split(' ')
            cat = line[0]
            did = int(line[1])
            if cat in cat_list:
                did_to_cat[did] = did_to_cat.get(did, []) + [cat]
        for did in list(did_to_cat.keys()):
            if len(did_to_cat[did]) > 1:
                del did_to_cat[did]

    dat_list = ['lyrl2004_tokens_test_pt0.dat',
                'lyrl2004_tokens_test_pt1.dat',
                'lyrl2004_tokens_test_pt2.dat',
                'lyrl2004_tokens_test_pt3.dat',
                'lyrl2004_tokens_train.dat']
    data = []
    target = []
    cat_to_cid = {'CCAT': 0, 'GCAT': 1, 'MCAT': 2, 'ECAT': 3}
    del did
    for dat in dat_list:
        with open(join(data_dir, dat)) as fin:
            for line in fin.readlines():
                if line.startswith('.I'):
                    if 'did' in locals():
                        assert doc != ''
                        if did in did_to_cat:
                            data.append(doc)
                            target.append(cat_to_cid[did_to_cat[did][0]])
                    did = int(line.strip().split(' ')[1])
                    doc = ''
                elif line.startswith('.W'):
                    assert doc == ''
                else:
                    doc += line

    assert len(data) == len(did_to_cat)

    x = CountVectorizer(dtype=np.float64, max_features=2000).fit_transform(data)
    y = np.asarray(target)

    from sklearn.feature_extraction.text import TfidfTransformer
    x = TfidfTransformer(norm='l2', sublinear_tf=True).fit_transform(x)
    x = x[:10000]
    y = y[:10000]
    x = np.asarray(x.todense()) * np.sqrt(x.shape[1])
    print('todense succeed')

    p = np.random.permutation(x.shape[0])
    x = x[p]
    y = y[p]
    print('permutation finished')

    assert x.shape[0] == y.shape[0]
    x = x.reshape((x.shape[0], x.size / x.shape[0]))
    np.save(join(data_dir, 'reutersidf10k.npy'), {'data': x, 'label': y})


def load_mnist():
    # the data, shuffled and split between train and test sets
    from keras.datasets import mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x = np.concatenate((x_train, x_test))
    y = np.concatenate((y_train, y_test))
    x = x.reshape((x.shape[0], -1))
    x = np.divide(x, 50.)  # normalize as it does in DEC paper
    print('MNIST samples', x.shape)
    return x, y


def load_usps(data_path='./data/usps'):
    import os
    if not os.path.exists(data_path+'/usps_train.jf'):
        if not os.path.exists(data_path+'/usps_train.jf.gz'):
            os.system('wget http://www-i6.informatik.rwth-aachen.de/~keysers/usps_train.jf.gz -P %s' % data_path)
            os.system('wget http://www-i6.informatik.rwth-aachen.de/~keysers/usps_test.jf.gz -P %s' % data_path)
        os.system('gunzip %s/usps_train.jf.gz' % data_path)
        os.system('gunzip %s/usps_test.jf.gz' % data_path)

    with open(data_path + '/usps_train.jf') as f:
        data = f.readlines()
    data = data[1:-1]
    data = [list(map(float, line.split())) for line in data]
    data = np.array(data)
    data_train, labels_train = data[:, 1:], data[:, 0]

    with open(data_path + '/usps_test.jf') as f:
        data = f.readlines()
    data = data[1:-1]
    data = [list(map(float, line.split())) for line in data]
    data = np.array(data)
    data_test, labels_test = data[:, 1:], data[:, 0]

    x = np.concatenate((data_train, data_test)).astype('float64')
    y = np.concatenate((labels_train, labels_test))
    print('USPS samples', x.shape)
    return x, y


def load_reuters(data_path='./data/reuters'):
    import os
    if not os.path.exists(os.path.join(data_path, 'reutersidf10k.npy')):
        print('making reuters idf features')
        make_reuters_data(data_path)
        print('reutersidf saved to ' + data_path)
    data = np.load(os.path.join(data_path, 'reutersidf10k.npy')).item()
    # has been shuffled
    x = data['data']
    y = data['label']
    x = x.reshape((x.shape[0], x.size / x.shape[0])).astype('float64')
    y = y.reshape((y.size,))
    print('REUTERSIDF10K samples', x.shape)
    return x, y

def unpickle(file):
  import pickle
  with open(file, 'rb') as fo:
    dict = pickle.load(fo, encoding='bytes')
  return dict

def load_cifar100(data_path='../cifar-100-python'):
  import os
  train = unpickle(os.path.join(data_path, 'train'))
  x = train[b'data']
  coarse_y = train[b'coarse_labels']
  fine_y = train[b'fine_labels']

  test = unpickle(os.path.join(data_path, 'test'))
  x = np.concatenate((x, test[b'data']))/255.
  coarse_y = np.concatenate((coarse_y, test[b'coarse_labels']))
  fine_y = np.concatenate((fine_y, test[b'fine_labels']))

  meta = unpickle(os.path.join(data_path, 'meta'))
  coarse_labels = meta[b'coarse_label_names']
  fine_labels = meta[b'fine_label_names']

  return x, coarse_y, fine_y, coarse_labels, fine_labels

def load_cifar10(data_path='../cifar-10-python'):
  import os
  for i in range(1,5):
    train = unpickle(os.path.join(data_path, 'data_batch_%s'%i))
    try:
      x = np.concatenate((x,train[b'data']))
      y = np.concatenate((y,train[b'labels']))
    except UnboundLocalError:
      x = train[b'data']
      y = train[b'labels']

  test = unpickle(os.path.join(data_path, 'test_batch'))
  x = np.concatenate((x, test[b'data']))/255.
  y = np.concatenate((y, test[b'labels']))

  meta = unpickle(os.path.join(data_path, 'batches.meta'))
  labels = meta[b'label_names']
  
  return x, y, labels

def load_stl10(data_path='../stl10_matlab'):
  import os
  import h5py
  import scipy.io as sio
  #data = h5py.File(os.path.join(data_path, 'train.mat'),'r')
  data = sio.loadmat(os.path.join(data_path, 'train.mat'))
  x = data['X']
  y = data['y']
  #data = h5py.File(os.path.join(data_path, 'test.mat'),'r')
  data = sio.loadmat(os.path.join(data_path, 'test.mat'))
  x = np.concatenate((x, data['X']))
  y = np.concatenate((y, data['y']))
  data = h5py.File(os.path.join(data_path, 'unlabeled.mat'),'r')
  x = np.concatenate((x, data['X'][:].T))/255.
  data.close()
  labeled_indices = range(len(y))
  return x, y, labeled_indices

def load_snhunters(data_path='../data'):
  import os
  import scipy.io as sio
  data = sio.loadmat(os.path.join(data_path,'3pi_20x20_skew2_signPreserveNorm.mat'))
  x = np.concatenate((data['X'], data['testX']))
  y = np.squeeze(np.concatenate((data['y'], data['testy'])))
  return x, y
