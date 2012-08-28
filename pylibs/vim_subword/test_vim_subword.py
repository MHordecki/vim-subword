
import unittest
import vim_subword

class MockVIMWrapper(object):
  def __init__(self, spec):
    assert spec.count('*') == 1

    self.linepos = spec.index('*')
    self.line = spec.replace('*', '')

  def delete(self, left, right):
    assert type(left) is int
    assert type(right) is int

    self.line = self.line[:left] + self.line[right+1:]
    if self.linepos < left:
      pass
    elif left <= self.linepos <= right:
      self.linepos = left
    elif self.linepos > right:
      self.linepos -= right-left+1

    self.linepos = max(0, min(len(self.line)-1, self.linepos))

  @property
  def spec(self):
    return self.line[:self.linepos] + '*' + self.line[self.linepos:]

class TestMockVIMWrapper(unittest.TestCase):
  def test_spec(self):
    assert MockVIMWrapper('lala*test').spec == 'lala*test'
    assert MockVIMWrapper('*test').spec == '*test'
    assert MockVIMWrapper('test*').spec == 'test*'

  def test_delete(self):
    def _test(spec, range, expected):
      ms = MockVIMWrapper(spec)
      ms.delete(*range)
      assert expected == ms.spec

    _test('foo*bar', (0, 1), 'o*bar')
    _test('*bar', (2, 2), '*ba')
    _test('foo*bar', (3, 5), 'fo*o')
    _test('foo*bar', (2, 3), 'fo*ar')

def test_get_subword_text_object():
  def _test(spec, expected):
    vimw = MockVIMWrapper(spec)
    word_range, sep_range = vim_subword.get_subword_text_object(vimw)
    ranges = [(word_range, '[]')]
    if sep_range is not None:
      ranges.append((sep_range, '{}'))
    res = []

    for i, ch in enumerate(vimw.line):
      for (left, right), (lbrace, rbrace) in ranges:
        if left == i:
          res.append(lbrace)
      res.append(ch)
      for (left, right), (lbrace, rbrace) in ranges:
        if right == i:
          res.append(rbrace)

    res = ''.join(res)
    assert expected == res

  _test('lol*aaa', '[lolaaa]')
  _test('*lolaaa', '[lolaaa]')
  _test('lolaa*a', '[lolaaa]')
  _test(' *foo_bar ', ' [foo]{_}bar ')
  _test(' f*oo_bar ', ' [foo]{_}bar ')
  _test(' fo*o_bar ', ' [foo]{_}bar ')
  _test(' foo_*bar ', ' foo{_}[bar] ')
  _test(' foo_b*ar ', ' foo{_}[bar] ')
  _test(' foo_ba*r ', ' foo{_}[bar] ')

  _test('(*foo_bar_heh)', '([foo]{_}bar_heh)')
  _test('(foo_ba*r_heh)', '(foo_[bar]{_}heh)')
  _test('(foo_bar_he*h)', '(foo_bar{_}[heh])')

  _test('Foo*BarLol', 'Foo[Bar]Lol')
  _test('FooB*arLol', 'Foo[Bar]Lol')
  _test('FooBa*rLol', 'Foo[Bar]Lol')


# In the following tests inital cursor position doesn't really matter.

def test_delete_inner_text_object():
  def _test(spec, text_object, expected):
    vimw = MockVIMWrapper(spec)
    vim_subword.delete_inner_text_object(text_object, vimw)
    assert expected == vimw.spec

  _test('*foobar', ((1, 2), None), 'f*bar')
  _test('*foobar', ((2, 2), (1, 1)), 'fo*bar')
  _test('*foobar', ((1, 1), (2, 2)), 'f*obar')
  _test('*foobar', ((4, 5), (3, 3)), 'foo*b')

def test_delete_outer_text_object():
  def _test(spec, text_object, expected):
    vimw = MockVIMWrapper(spec)
    vim_subword.delete_outer_text_object(text_object, vimw)
    assert expected == vimw.spec

  _test('*foobar', ((1, 2), None), 'f*bar')
  _test('*foobar', ((2, 2), (1, 1)), 'f*bar')
  _test('*foobar', ((1, 1), (2, 2)), 'f*bar')

