from matplotlib import pyplot as plt

def check_do_plot(func):
  def inner(self, *args, **kwargs):
    if self.do_plot:
      return func(self, *args, **kwargs)
    else:
      pass
  return inner

class Plotter(object):
  def __init__(self, plot=True):
    self.counter = [1]
    self.do_plot = plot

  @check_do_plot
  def plot_one(self, row, col, img):
    p = plt.subplot(row, col, self.counter[0])
    p.axes.get_xaxis().set_visible(False)
    p.axes.get_yaxis().set_visible(False)
    plt.imshow(img)
    self.counter[0] += 1

  @check_do_plot
  def end(self):
    plt.gcf().subplots_adjust(hspace=0.05, wspace=0,
                              left=0, bottom=0, right=1, top=0.98)
    plt.axis('off')
    plt.show()

  @check_do_plot
  def plot_mesh(self, points, tri, color='k'):
    """ plot triangles """
    for tri_indices in tri.simplices:
      t_ext = [tri_indices[0], tri_indices[1], tri_indices[2], tri_indices[0]]
      plt.plot(points[t_ext, 0], points[t_ext, 1], color)
