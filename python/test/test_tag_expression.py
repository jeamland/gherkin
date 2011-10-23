import unittest

from nose import tools

from gherkin.tag_expression import TagExpression

class TestTagExpressionNoTags(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression([])
    
    def test_should_match_foo(self):
        assert self.e.eval(['@foo'])
    
    def test_should_match_empty_tags(self):
        assert self.e.eval([])
    
class TestTagExpressionFoo(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['@foo'])
    
    def test_should_match_foo(self):
        assert self.e.eval(['@foo'])
    
    def test_should_not_match_bar(self):
        assert not self.e.eval(['@bar'])
    
    def test_should_not_match_no_tags(self):
        assert not self.e.eval([])

class TestTagExpressionNotFoo(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['~@foo'])
    
    def test_should_match_bar(self):
        assert self.e.eval(['@bar'])
    
    def test_should_not_match_foo(self):
        assert not self.e.eval(['@foo'])

class TestTagExpressionFooOrBar(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['@foo,@bar'])
    
    def test_should_match_foo(self):
        assert self.e.eval(['@foo'])

    def test_should_match_bar(self):
        assert self.e.eval(['@bar'])
    
    def test_should_not_match_zap(self):
        assert not self.e.eval(['@zap'])

class TestTagExpressionFooOrBarAndNotZap(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['@foo,@bar', '~@zap'])
    
    def test_should_match_foo(self):
        assert self.e.eval(['@foo'])
        
    def test_should_not_match_foo_zap(self):
        assert not self.e.eval(['@foo', '@zap'])

class TestTagExpressionFoo3OrNotBar4AndZap5(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression(['@foo:3,~@bar', '@zap:5'])
    
    def test_should_count_tags_for_positive_tags(self):
        tools.eq_(self.e.limits, {'@foo': 3, '@zap': 5})
    
    def test_should_match_foo_zap(self):
        assert self.e.eval(['@foo', '@zap'])

class TestTagExpressionParsing(unittest.TestCase):
    def setUp(self):
        self.e = TagExpression([' @foo:3 , ~@bar ', ' @zap:5 '])
    
    def test_should_have_limits(self):
        tools.eq_(self.e.limits, {'@zap': 5, '@foo': 3})

class TestTagExpressionTagLimits(unittest.TestCase):
    def test_should_be_counted_for_negative_tags(self):
        e = TagExpression(['~@todo:3'])
        tools.eq_(e.limits, {'@todo': 3})
    
    def test_should_be_counted_for_positive_tags(self):
        e = TagExpression(['@todo:3'])
        tools.eq_(e.limits, {'@todo': 3})
    
    def test_should_raise_an_error_for_inconsistent_limits(self):
        with tools.assert_raises(Exception):
            e = TagExpression(['@todo:3', '~@todo:4'])
    
    def test_should_allow_duplicate_consistent_limits(self):
        e = TagExpression(['@todo:3', '~@todo:3'])
        tools.eq_(e.limits, {'@todo': 3})
        