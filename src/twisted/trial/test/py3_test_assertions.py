# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests specific to Python 3 to add to
L{twisted.trial.unittest.test.test_assertions}.
"""

from __future__ import division, absolute_import

from asyncio import Future

from twisted.python.failure import Failure
from twisted.trial import unittest
from twisted.internet.defer import Deferred, fail, succeed


class ResultOfCoroutineAssertionsTests(unittest.SynchronousTestCase):
    """
    Tests for L{SynchronousTestCase.successResultOf},
    L{SynchronousTestCase.failureResultOf}, and
    L{SynchronousTestCase.assertNoResult} when given a coroutine.
    """

    result = object()
    exception = Exception("Bad times")


    async def successResult(self):
        return self.result


    async def noCurrentResult(self):
        await Future()


    async def raisesException(self):
        raise self.exception


    def test_withoutResult(self):
        """
        L{SynchronousTestCase.successResultOf} raises
        L{SynchronousTestCase.failureException} when called with a coroutine
        with no current result.
        """
        self.assertRaises(
            self.failureException, self.successResultOf, self.noCurrentResult()
        )


    def test_successResultOfWithException(self):
        """
        L{SynchronousTestCase.successResultOf} raises
        L{SynchronousTestCase.failureException} when called with a coroutine
        that raises an exception.
        """
        self.assertRaises(
            self.failureException, self.successResultOf, self.raisesException()
        )


    def test_successResultOfWithFailureHasTraceback(self):
        """
        L{SynchronousTestCase.successResultOf} raises a
        L{SynchronousTestCase.failureException} that has the original failure
        traceback when called with a coroutine with a failure result.
        """
        try:
            self.successResultOf(self.raisesException())
        except self.failureException as e:
            self.assertIn(self.failure.getTraceback(), str(e))


    def test_failureResultOfWithoutResult(self):
        """
        L{SynchronousTestCase.failureResultOf} raises
        L{SynchronousTestCase.failureException} when called with a coroutine
        with no current result.
        """
        self.assertRaises(
            self.failureException, self.failureResultOf, self.noCurrentResult()
        )


    def test_failureResultOfWithSuccess(self):
        """
        L{SynchronousTestCase.failureResultOf} raises
        L{SynchronousTestCase.failureException} when called with a coroutine
        with a success result.
        """
        self.assertRaises(
            self.failureException, self.failureResultOf, self.successResult()
        )


    def test_failureResultOfWithWrongFailure(self):
        """
        L{SynchronousTestCase.failureResultOf} raises
        L{SynchronousTestCase.failureException} when called with a coroutine
        that raises an exception that was not expected.
        """
        self.assertRaises(
            self.failureException,
            self.failureResultOf, self.raisesException(), KeyError
        )


    def test_failureResultOfWithWrongExceptionOneExpectedException(self):
        """
        L{SynchronousTestCase.failureResultOf} raises
        L{SynchronousTestCase.failureException} when called with a coroutine
        that raises an exception with a failure type that was not expected, and
        the L{SynchronousTestCase.failureException} message contains the
        original failure exception as well as the expected exception type.
        """
        try:
            self.failureResultOf(self.raisesException(), KeyError)
        except self.failureException as e:
            self.assertIn(self.failure.getTraceback(), str(e))
            self.assertIn(
                "Failure of type ({0}.{1}) expected on".format(
                    KeyError.__module__, KeyError.__name__
                ),
                str(e)
            )


    def test_failureResultOfWithWrongExceptionMultiExpectedExceptions(self):
        """
        L{SynchronousTestCase.failureResultOf} raises
        L{SynchronousTestCase.failureException} when called with a coroutine
        that raises an exception of a type that was not expected, and the
        L{SynchronousTestCase.failureException} message contains the original
        exception traceback as well as the expected exception types in the
        error message.
        """
        try:
            self.failureResultOf(self.raisesException(), KeyError, IOError)
        except self.failureException as e:
            self.assertIn(self.failure.getTraceback(), str(e))
            self.assertIn(
                "Failure of type ({0}.{1} or {2}.{3}) expected on".format(
                    KeyError.__module__, KeyError.__name__,
                    IOError.__module__, IOError.__name__,
                ),
                str(e)
            )


    def test_successResultOfWithSuccessResult(self):
        """
        When passed a coroutine which currently has a result (ie, if converted
        into a L{Deferred}, L{Deferred.addCallback} would cause the added
        callback to be called before C{addCallback} returns),
        L{SynchronousTestCase.successResultOf} returns that result.
        """
        self.assertIdentical(
            self.result, self.successResultOf(self.successResult())
        )


    def test_failureResultOfWithExpectedFailureResult(self):
        """
        When passed a coroutine which currently has an exception result (ie, if
        converted into a L{Deferred}, L{Deferred.addErrback} would cause the
        added errback to be called before C{addErrback} returns),
        L{SynchronousTestCase.failureResultOf} returns a L{Failure} containing
        that exception, if the exception type is expected.
        """
        self.assertIdentical(
            self.failure,
            self.failureResultOf(
                self.raisesException(), self.failure.type, KeyError
            )
        )


    def test_failureResultOfWithFailureResult(self):
        """
        When passed a coroutine which currently has an exception result (ie, if
        converted into a L{Deferred}, L{Deferred.addErrback} would cause the
        added errback to be called before C{addErrback} returns),
        L{SynchronousTestCase.failureResultOf} returns returns a L{Failure}
        containing that exception.
        """
        self.assertIdentical(
            self.failure, self.failureResultOf(self.raisesException())
        )


    def test_assertNoResultSuccess(self):
        """
        When passed a coroutine which currently has a success result (see
        L{test_withSuccessResult}), L{SynchronousTestCase.assertNoResult}
        raises L{SynchronousTestCase.failureException}.
        """
        self.assertRaises(
            self.failureException, self.assertNoResult, self.successResult()
        )


    def test_assertNoResultFailure(self):
        """
        When passed a coroutine which currently has an exception result (see
        L{test_withFailureResult}), L{SynchronousTestCase.assertNoResult}
        raises L{SynchronousTestCase.failureException}.
        """
        self.assertRaises(
            self.failureException, self.assertNoResult, self.raisesException()
        )


    def test_assertNoResult(self):
        """
        When passed a coroutine with no current result,
        L{SynchronousTestCase.assertNoResult} does not raise an exception.
        """
        self.assertNoResult(self.noCurrentResult())


    def test_assertNoResultPropagatesSuccess(self):
        """
        When passed a coroutine awaiting a L{Deferred} with no current result,
        which is then fired with a success result,
        L{SynchronousTestCase.assertNoResult} doesn't modify the result of the
        L{Deferred}.
        """
        d = Deferred()

        async def noCurrentResult():
            return await d

        c = noCurrentResult()
        self.assertNoResult(c)
        d.callback(self.result)
        self.assertEqual(self.result, self.successResultOf(c))


    def test_assertNoResultPropagatesLaterFailure(self):
        """
        When passed a coroutine awaiting a L{Deferred} with no current result,
        which is then fired with a L{Failure} result,
        L{SynchronousTestCase.assertNoResult} doesn't modify the result of the
        L{Deferred}.
        """
        f = Failure(self.exception)
        d = Deferred()

        async def noCurrentResult():
            return await d

        c = noCurrentResult()
        self.assertNoResult(c)
        d.errback(f)
        self.assertEqual(f, self.failureResultOf(c))


    def test_assertNoResultSwallowsImmediateFailure(self):
        """
        When passed a L{Deferred} which currently has a L{Failure} result,
        L{SynchronousTestCase.assertNoResult} changes the result of the
        L{Deferred} to a success.
        """
        d = fail(self.failure)

        async def raisesException():
            return await d

        c = raisesException()
        try:
            self.assertNoResult(c)
        except self.failureException:
            pass
        self.assertEqual(None, self.successResultOf(c))
