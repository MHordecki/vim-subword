"""
vim_subword by Mike Hordecki

Subword text objects for vim.

This code is fairly generic, so feel free to use it
for your own purposes.

Text object is an implicit data structure used throughout this module.
You can define it like this:
    (word_range, separator_range)
where word_range is 2-tuple of numbers that define an inclusive range
of characters in the current line that are the text object in question, and
separator_range is the same thing but for the separator character(s) between
subsequent text objects. For the sake of being similar to builtin vim text
objects, separator AFTER a text object is preferred, if possible [1].

    [1] Run ``vaw`` in vim and see which space gets selected.
"""

import functools


class VimWrapper(object):
  """Wraps vim in a pleasant API.

  This class deals with single lines only.
  """

  def __init__(self, vim=None):
    """
    :param vim: vim module. Optional, defaults to "import vim".
    """
    if vim is None:
      import vim
    self.vim = vim
    self.line = vim.current.line

  @property
  def line(self): return self.vim.current.line

  @line.setter
  def line(self, value): self.vim.current.line = value

  @property
  def linepos(self): return self.vim.current.window.cursor[1]

  @linepos.setter
  def linepos(self, value):
    lineidx, _ = self.vim.current.window.cursor
    self.vim.current.window.cursor = (lineidx, value)

  def delete(self, left, right):
    "Delete the given index range(inclusive) in the current line."
    assert type(left) is int
    assert type(right) is int

    new_line = self.line[:left] + self.line[right+1:]
    linepos = self.linepos
    if linepos < left:
      pass
    elif left <= linepos <= right:
      linepos = left
    elif linepos > right:
      linepos -= right-left+1

    self.line = new_line
    self.linepos = linepos

  def go_to_insert_mode(self):
    self.vim.command('startinsert')


def get_subword_text_object(vimw=None):
  """Returns a text object - subword that the cursor is currently pointing to.

  For the definition of a text object, see the docstring for this module.
  """
  if vimw is None: vimw = VimWrapper()

  ok = 'zxcvbnmlkjhgfdsaqwertyuiop0987654321'
  bad = 'ZXCVBNMLKJHGFDSAQWERTYUIOP_'
  def walk(txt, start, stride):
    """
    :param txt: A string
    :param stride: Direction in which to walk, either -1 or 1.
    :param start: Start index
    """
    idx = start
    while 0 <= idx < len(txt):
      if txt[idx] not in ok:
        return idx-stride
      idx += stride
    return idx-stride
  left = walk(vimw.line, vimw.linepos, -1)
  right = walk(vimw.line, vimw.linepos+1, 1)

  if left-1 >= 0 and vimw.line[left-1].isupper():
    return (left-1, right), None
  if right+1 < len(vimw.line) and vimw.line[right+1] in bad:
    return (left, right), (right+1, right+1)
  if left-1 >= 0 and vimw.line[left-1] in bad:
    return (left, right), (left-1, left-1)
  return (left, right), None


def delete_inner_text_object(text_object=None, vimw=None,
                             text_object_factory=None):
  if vimw is None: vimw = VimWrapper()
  assert text_object or text_object_factory
  if text_object is None:
    text_object = text_object_factory(vimw)

  word_range, sep_range = text_object
  if sep_range is None:
    wl, wr = word_range
    vimw.linepos = wl
    vimw.delete(wl, wr)
  else:
    sl, sr = sep_range
    wl, wr = word_range
    assert not (wl <= sl <= wr or wl <= sr <= wr)
    if sl > wr:
      vimw.linepos = sl
    else:
      vimw.linepos = wl
    vimw.delete(wl, wr)

def delete_outer_text_object(text_object=None, vimw=None, text_object_factory=None):
  if vimw is None: vimw = VimWrapper()
  assert text_object or text_object_factory
  if text_object is None:
    text_object = text_object_factory(vimw)

  word_range, sep_range = text_object
  if sep_range is None:
    return delete_inner_text_object(vimw=vimw, text_object=text_object)

  sl, sr = sep_range
  wl, wr = word_range
  assert not (wl <= sl <= wr or wl <= sr <= wr)
  vimw.linepos = sl
  if sl > wr:
    vimw.delete(sl, sr)
    vimw.delete(wl, wr)
  else:
    vimw.delete(wl, wr)
    vimw.delete(sl, sr)

def change_inner_text_object(text_object=None, vimw=None, text_object_factory=None):
  if vimw is None: vimw = VimWrapper()
  assert text_object or text_object_factory
  if text_object is None:
    text_object = text_object_factory(vimw)

  delete_inner_text_object(text_object=text_object, vimw=vimw)
  vimw.go_to_insert_mode()

def change_outer_text_object(text_object=None, vimw=None, text_object_factory=None):
  if vimw is None: vimw = VimWrapper()
  assert text_object or text_object_factory
  if text_object is None:
    text_object = text_object_factory(vimw)

  delete_outer_text_object(text_object=text_object, vimw=vimw)
  vimw.go_to_insert_mode()


delete_inner_subword = functools.partial(delete_inner_text_object,
                                         text_object_factory=get_subword_text_object)
delete_outer_subword = functools.partial(delete_outer_text_object,
                                         text_object_factory=get_subword_text_object)
change_inner_subword = functools.partial(change_inner_text_object,
                                         text_object_factory=get_subword_text_object)
change_outer_subword = functools.partial(change_outer_text_object,
                                         text_object_factory=get_subword_text_object)


