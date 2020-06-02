import logging
import time
import json
import uuid
import requests
import psutil
import azure.functions as func
import traceback
import random
import platform

from math import sqrt
from functools import reduce
import collections
import pandas as pd
import numpy as np

import calendar
import sys
from datetime import datetime, timedelta
from datetime import tzinfo as dt_tzinfo
from math import trunc

from dateutil import tz as dateutil_tz
from dateutil.relativedelta import relativedelta

from arrow import formatter, locales, parser, util


if 'instance_identifier' not in locals():
    instance_identifier = str(uuid.uuid4())


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # req: HTTPRequest provided by azure

    # get start time
    start_time = time.time()
    # we create an UUID to ensure that the function has
    # to do some arbitrary computation such that responses cannot
    # be cached, as well for identifying unique invocations
    invocation_uuid = str(uuid.uuid4())
    # unique name of this function
    function_name = 'monolith'

    # whoami?
    identifier = f'{function_name}-{invocation_uuid}'

    try:
        # parse request json
        req_json = json.loads(req.get_body())

        seed = req_json['seed']
        random.seed(seed)

         # list of functions that will be called dependent on the seed given
        functions = [
            ('matrix_mult', lambda x: matrix_mult(x,x)),
            ('fib', lambda x: fib() ),
            ('makeTree', lambda x: make_tree(TreeNode(random.randint(0,100)),x)),
            ('isSymmetric', lambda x: isSymmetric(make_tree(TreeNode(random.randint(0,10)),x))),
            ('levelOrder', lambda x: levelOrder(make_tree(TreeNode(random.randint(0,10)),x))),
            ('maxDepth', lambda x: maxDepth(make_tree(TreeNode(random.randint(0,10)),x))),
            ('levelOrderBottom', lambda x: levelOrderBottom(make_tree(TreeNode(random.randint(0,10)),x))),
            ('sortedArrayToBST', lambda x: sortedArrayToBST([n for n in range(x)])),
            ('zigzagLevelOrder', lambda x: zigzagLevelOrder(make_tree(TreeNode(random.randint(0,10)),x))),
            ('sortedListToBST', lambda x: sortedListToBST(makeListNode(x))),
            ('isBalanced', lambda x: isBalanced(make_tree(TreeNode(random.randint(0,10)),x))),
            ('minDepth', lambda x: minDepth(make_tree(TreeNode(random.randint(0,10)),x))),
            ('flatten', lambda x: flatten(make_tree(TreeNode(random.randint(0,10)),x))),
            ('maxPathSum', lambda x: maxPathSum(make_tree(TreeNode(random.randint(0,10)),x))),
            ('preorderTraversal', lambda x: preorderTraversal(make_tree(TreeNode(random.randint(0,10)),x))),
            ('rightSideView', lambda x: rightSideView(make_tree(TreeNode(random.randint(0,10)),x))),
            ('dummie_webpage', lambda x: dummie_webpage()),
            ('docker_documentation', lambda x: docker_documentation()),
            ('use_arrow', lambda x: use_arrow()),
            ('pandas_numpy', lambda x: pandas_numpy(x)),
        ]

        # create a dict that will be parsed to json
        body = {
            identifier: {
                "identifier": identifier,
                "uuid": invocation_uuid,
                "function_name": function_name,
                "function_cores": psutil.cpu_count(),
            },
        }



        # make sure that things are working...
        if req_json['StatusCode'] != 200:
            raise StatusCodeException(
                'StatusCode: '+str(req_json['StatusCode']))

        if 'parent' not in req_json:
            # if first in chain mark as root
            body[identifier]['parent'] = 'root'
        else:
            body[identifier]['parent'] = req_json['parent']

        # set level if root in invocation tree
        if 'level' not in req_json:
            body[identifier]['level'] = 0
        else:
            body[identifier]['level'] = req_json['level'] + 1

        # if request contains a sleep argument, then sleep for that amount
        # and log the amount of time slept
        if 'sleep' in req_json:
            time.sleep(req_json['sleep'])
            body[identifier]['sleep'] = req_json['sleep']
        else:
            body[identifier]['sleep'] = 0.0

        if 'throughput_time' in req_json:
            random.seed(req_json['throughput_time'] * 100)
            process_time_start = time.process_time()
            throughput_start = time.time()
            throughput = []

            while(time.time()-throughput_start < req_json['throughput_time']):
                throughput.append(random.random())
            throughput_process_time = time.process_time() - process_time_start

            body[identifier]['throughput_running_time'] = time.time() - \
                throughput_start
            body[identifier]['throughput'] = len(throughput)
            body[identifier]['throughput_time'] = req_json['throughput_time']
            body[identifier]['throughput_process_time'] = throughput_process_time
            body[identifier]['random_seed'] = req_json['throughput_time'] * 100
        else:
            body[identifier]['throughput'] = 0.0
            body[identifier]['throughput_running_time'] = None
            body[identifier]['throughput_time'] = None
            body[identifier]['throughput_process_time'] = None
            body[identifier]['random_seed'] = None

        # add python version metadata
        body[identifier]['python_version'] = platform.python_version()
        # add total memory of pod to metadata
        body[identifier]['memory'] = psutil.virtual_memory()[0]
        # log instance identifier
        body[identifier]['instance_identifier'] = instance_identifier

        # ==============================================================


        def make_matrix(x,y):
            matrix = []
            for i in range(x):
                lis = []
                for n in range(y):
                    lis.append(random.randint(0,100))
                matrix.append(lis)
            return matrix


        def matrix_mult(n,z):

            throughput_t_start = time.time()
            process_t_start = time.process_time()

            matrix1 = make_matrix(n,z)
            matrix2 = make_matrix(n,z)
            multiplied = [ [ sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*matrix2) ] for X_row in matrix1]
            result = reduce(lambda x,y: reduce( lambda a,b: a+b,y),multiplied)

            process_time = time.process_time() - process_t_start

            body[identifier]['process_time_matrix'] = process_time
            body[identifier]['running_time_matrix'] = time.time() - throughput_t_start

            return result

        def fib():
            n = random.randint(0,20)
            return ((1+sqrt(5))**n-(1-sqrt(5))**n)/(2**n*sqrt(5))

        class TreeNode(object):
            def __init__(self, val=0, left=None, right=None):
                        self.val = val
                        self.left = left
                        self.right = right

        def make_tree(node:TreeNode,n:int):
            if n == 0:
                return node
            node.left = make_tree(TreeNode(random.randint(0,100)),n-1)
            node.right = make_tree(TreeNode(random.randint(0,100)),n-1)
            return node

        class ListNode(object):
            def __init__(self, val=0, next=None):
                self.val = val
                self.next = next

        def makeListNode(n:int):
            head = ListNode(random.randint(0,100))
            node = head
            for i in range(n):
                n = ListNode(random.randint(0,100))
                node.next = n
                node = node.next
            return head


        def compare(left, right):
            if not left and not right:
                return True
            if left and right:
                if left.val != right.val:
                    return False
                return compare(left.left, right.right) and compare(left.right, right.left)
            return False

        def isSymmetric(root):
            if not root:
                return True
            return compare(root.left, root.right)

        def levelOrder(root: TreeNode):
            if not root:
                return []
            q = [root]
            level = [[root.val]]
            while q:
                size = len(q)
                l = []
                while size:
                    front = q.pop(0)
                    size-=1

                    if front.left:
                        q.append(front.left)
                        l+=[front.left.val]
                    if front.right:
                        q.append(front.right)
                        l+=[front.right.val]
                if len(l):
                    level.append(l)

            return level

        def helper(Node):
            if Node==None:
                return 0
            return max(helper(Node.left),helper(Node.right))+1

        def maxDepth(root: TreeNode) -> int:
            if root==None:
                return 0
            else:
                return helper(root)

        def levelOrderBottom(root: TreeNode):
            res = []
            def helper(node, level):
                if node is None:
                    return
                if level == len(res):
                    res.append([])
                res[level].append(node.val)
                helper(node.left, level + 1)
                helper(node.right, level + 1)
            helper(root, 0)
            res.reverse()
            return res

        def sortedArrayToBST(nums:list) -> TreeNode:
            if not nums:
                return(None)
            middleIndex = len(nums)//2
            root = TreeNode(nums[middleIndex])
            root.left = sortedArrayToBST(nums[:middleIndex])
            if middleIndex < len(nums)-1:
                root.right = sortedArrayToBST(nums[middleIndex+1:])
            return(root)

        def zigzagLevelOrder(root: TreeNode):
            if not root:
                return []

            res = [[root.val]]
            queue = collections.deque([root])
            level = 1

            while True:
                curr = []
                while queue:
                    node = queue.popleft()
                    if node.left:
                        curr.append(node.left)
                    if node.right:
                        curr.append(node.right)
                queue.extend(curr)
                if not queue:
                    break
                if level % 2 == 1:
                    res.append([node.val for node in curr][::-1])
                else:
                    res.append([node.val for node in curr])
                level += 1

            return res

        def sortedListToBST(head):
            def build(arr):
                if not arr:
                    return None

                start, end = 0, len(arr)
                mid = int(len(arr)/2)

                node = TreeNode(arr[mid])
                node.left = build(arr[start:mid])
                node.right = build(arr[mid+1:end])

                return node

            arr = []
            while head:
                arr.append(head.val)
                head = head.next

            return build(arr)

        def isBalanced(root: TreeNode) -> bool:
            def check_balanced(node):
                if not node: return [0,True]
                left = check_balanced(node.left)
                left_height = left[0]+1
                left_bool = left[1]
                right = check_balanced(node.right)
                right_height = right[0]+1
                right_bool = right[1]
                total_bool = left_bool and right_bool and abs(left_height-right_height)<=1
                return [max(left_height,right_height),total_bool]
            check = check_balanced(root)
            return check[1]

        def minDepth(root: TreeNode) -> int:
            if root is None:
                return 0
            if root.left and root.right:
                return min(minDepth(root.left),minDepth(root.right)) + 1
            else:
                return max(minDepth(root.left),minDepth(root.right)) + 1

        def flatten(root: TreeNode) -> None:
            """
            Do not return anything, modify root in-place instead.
            """
            if not root:
                return None

            flattened_left = flatten(root.left)
            flattened_right = flatten(root.right)

            root.left = None
            root.right = flattened_left

            it = root
            while it.right:
                it = it.right

            it.right = flattened_right

            return root

        def maxPathSum(root: TreeNode) -> int:
            res = float('-inf')
            def dfs(node):
                nonlocal res
                if not node:
                    return 0
                s = node.val
                sleft = dfs(node.left)
                sright = dfs(node.right)
                max_path = max(s, s + sleft, s + sright)
                tree_sum = s + sleft + sright
                res = max(res, max_path, tree_sum)
                return max_path
            dfs(root)
            return res

        def preorderTraversal(root: TreeNode):
            ans = []
            def fn(node):
                if not node: return
                ans.append(node.val)
                fn(node.left)
                fn(node.right)

            fn(root)
            return ans

        def rightSideView(root):
            """
            :type root: TreeNode
            :rtype: List[int]
            """
            if not root:
                return

            right = left = []
            if root.right:
                right = rightSideView(root.right)
            right = [root.val] + right
            if root.left:
                left = rightSideView(root.left)
            left = [root.val] + left

            if len(right) >= len(left):
                return right
            ex = left[len(right):]
            res = right + ex
            return res

        def dummie_webpage():
            strings = ['pony','derp','unicorn','foo','bar']
            text = f"""<html>
            <!-- Text between angle brackets is an HTML tag and is not displayed.
            Most {strings[random.randint(0,len(strings)-1)]}, such as the HTML and /HTML tags that surround the contents of
            a page, come in pairs; some tags, like HR, for a horizontal rule, stand
            alone. Comments, such as the text you're reading, are not displayed when
            the Web page is shown. The information between the HEAD and /HEAD tags is
            not displayed. The information between the BODY and /BODY tags is displayed.-->
            <head>
            <title>Enter a title, {strings[random.randint(0,len(strings)-1)]} displayed at the top of the window.</title>
            </head>
            <!-- The information between the BODY and /BODY tags is displayed.-->
            <body>
            <h1>Enter the main heading, {strings[random.randint(0,len(strings)-1)]} usually the same as the title.</h1>
            <p>Be <b>bold</b> in stating your key points. Put them in a list: </p>
            <ul>
            <li>The first item in your list</li>
            <li>The second item; <i>italicize</i> key words</li>
            </ul>
            <p>Improve your image by including an image. {strings[random.randint(0,len(strings)-1)]} </p>
            <p><img src="http://www.mygifs.com/CoverImage.gif" alt="A Great HTML Resource"></p>
            <p>Add a link to your favorite <a href="https://www.dummies.com/">Web site</a>.
            Break up your page with a horizontal rule or two. </p>
            <hr>
            <p>Finally, link to {strings[random.randint(0,len(strings)-1)]} <a href="page2.html">another page</a> in your own Web site.</p>
            <!-- And add a copyright notice.-->
            <p>&#169; Wiley Publishing, 2011</p>
            </body>
            </html>"""
            rand = random.randint(0,len(text)-100)
            sliced = text[rand:rand+100]
            return sliced

        def docker_documentation():
            insert_vals = ['pony','derp','unicorn','foo','bar', 42, 'tinfoilhat']
            text = f""" Docker Desktop overview
            Estimated reading time: 2 minutes

            Docker Desktop is an easy-to-install {insert_vals[random.randint(0,len(insert_vals)-1)]} application for your Mac or Windows environment that enables you to build and share containerized applications and microservices. Docker Desktop includes Docker Engine, Docker CLI client, Docker Compose, Notary, Kubernetes, and Credential Helper.

            Docker Desktop works with your choice of development tools and languages and gives you access to a vast library of certified images and templates in Docker Hub. This enables development teams to extend their environment to rapidly auto-build, continuously integrate and collaborate using a secure repository.

            Some of the key features {insert_vals[random.randint(0,len(insert_vals)-1)]} of Docker Desktop include:

            Ability to containerize and share any application on any cloud platform, in multiple languages and frameworks
            Easy installation and setup of a complete Docker development environment

            Includes the latest version of Kubernetes
            Automatic updates to keep {insert_vals[random.randint(0,len(insert_vals)-1)]}you up to date and secure
            On Windows, the ability to toggle between Linux and Windows Server environments to build applications
            Fast and reliable performance with native Windows Hyper-V virtualization
            Ability to work natively on Linux through WSL 2 on Windows machines
            Volume mounting for code and data, including file change notifications and easy access to running
            containers on the localhost network
            In-container development and debugging with supported IDEs

            Download and install {str([i for i in range(random.randint(0,100))])}

            Docker Desktop is available for Mac and Windows. For download information, system requirements,
            and installation instructions, see:
                {insert_vals[random.randint(0,len(insert_vals)-1)]}
                Install Docker Desktop on Mac
                Install Docker Desktop on Windows

            Get started

            For information on how to get to get started with Docker Desktop and to learn about various UI
            options and their usage, see:
            {insert_vals[random.randint(0,len(insert_vals)-1)]}
                Get started with Docker Desktop on Mac
                Get started with Docker Desktop on Windows

            Stable and Edge versions

            Docker Desktop offers Stable and Edge download channels.

            The Stable release provides {insert_vals[random.randint(0,len(insert_vals)-1)]} a general
            availability release-ready installer for a fully baked and tested, more reliable app.
            The Stable version of Docker Desktop includes the latest released version of Docker Engine.
            The release schedule is synced every three months for major releases, with patch releases to fix minor issues,
            and to stay up to date with Docker Engine as required. You can choose to opt out of the usage statistics
            and telemetry data on the Stable channel.

            Docker Desktop Edge release is our preview version. It offers an installer with the
            latest features and comes with the experimental features turned on. When using the Edge
            release, bugs, crashes, and issues can occur as the new features may not be fully tested.
            However, you get a chance to preview new functionality, experiment, and provide feedback as
            Docker Desktop evolves. Edge releases are typically more frequent than Stable releases.
            Telemetry data and usage statistics are sent by default on the Edge version. """

            rand = random.randint(0,len(text)-100)
            sliced = text[rand:rand+100]
            return sliced

        class Arrow2(object):
            """An :class:`Arrow2 <Arrow2.arrow.Arrow>` object.
            Implements the ``datetime`` interface, behaving as an aware ``datetime`` while implementing
            additional functionality.
            :param year: the calendar year.
            :param month: the calendar month.
            :param day: the calendar day.
            :param hour: (optional) the hour. Defaults to 0.
            :param minute: (optional) the minute, Defaults to 0.
            :param second: (optional) the second, Defaults to 0.
            :param microsecond: (optional) the microsecond. Defaults 0.
            :param tzinfo: (optional) A timezone expression.  Defaults to UTC.
            .. _tz-expr:
            Recognized timezone expressions:
                - A ``tzinfo`` object.
                - A ``str`` describing a timezone, similar to 'US/Pacific', or 'Europe/Berlin'.
                - A ``str`` in ISO 8601 style, as in '+07:00'.
                - A ``str``, one of the following:  'local', 'utc', 'UTC'.
            Usage::
                >>> import arrow
                >>> arrow.Arrow(2013, 5, 5, 12, 30, 45)
                <Arrow2 [2013-05-05T12:30:45+00:00]>
            """

            resolution = datetime.resolution

            _ATTRS = ["year", "month", "day", "hour", "minute", "second", "microsecond"]
            _ATTRS_PLURAL = ["{}s".format(a) for a in _ATTRS]
            _MONTHS_PER_QUARTER = 3
            _SECS_PER_MINUTE = float(60)
            _SECS_PER_HOUR = float(60 * 60)
            _SECS_PER_DAY = float(60 * 60 * 24)
            _SECS_PER_WEEK = float(60 * 60 * 24 * 7)
            _SECS_PER_MONTH = float(60 * 60 * 24 * 30.5)
            _SECS_PER_YEAR = float(60 * 60 * 24 * 365.25)

            def __init__(
                self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
            ):
                if tzinfo is None:
                    tzinfo = dateutil_tz.tzutc()
                # detect that tzinfo is a pytz object (issue #626)
                elif (
                    isinstance(tzinfo, dt_tzinfo)
                    and hasattr(tzinfo, "localize")
                    and hasattr(tzinfo, "zone")
                    and tzinfo.zone
                ):
                    tzinfo = parser.TzinfoParser.parse(tzinfo.zone)
                elif util.isstr(tzinfo):
                    tzinfo = parser.TzinfoParser.parse(tzinfo)

                self._datetime = datetime(
                    year, month, day, hour, minute, second, microsecond, tzinfo
                )

            # factories: single object, both original and from datetime.

            @classmethod
            def now(cls, tzinfo=None):
                """Constructs an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object, representing "now" in the given
                timezone.
                :param tzinfo: (optional) a ``tzinfo`` object. Defaults to local time.
                Usage::
                    >>> Arrow2.now('Asia/Baku')
                    <Arrow2 [2019-01-24T20:26:31.146412+04:00]>
                """

                if tzinfo is None:
                    tzinfo = dateutil_tz.tzlocal()
                dt = datetime.now(tzinfo)

                return cls(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,
                    dt.tzinfo,
                )

            @classmethod
            def utcnow(cls):
                """ Constructs an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object, representing "now" in UTC
                time.
                Usage::
                    >>> Arrow2.utcnow()
                    <Arrow2 [2019-01-24T16:31:40.651108+00:00]>
                """

                dt = datetime.now(dateutil_tz.tzutc())

                return cls(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,
                    dt.tzinfo,
                )

            @classmethod
            def fromtimestamp(cls, timestamp, tzinfo=None):
                """ Constructs an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object from a timestamp, converted to
                the given timezone.
                :param timestamp: an ``int`` or ``float`` timestamp, or a ``str`` that converts to either.
                :param tzinfo: (optional) a ``tzinfo`` object.  Defaults to local time.
                """

                if tzinfo is None:
                    tzinfo = dateutil_tz.tzlocal()
                elif util.isstr(tzinfo):
                    tzinfo = parser.TzinfoParser.parse(tzinfo)

                if not util.is_timestamp(timestamp):
                    raise ValueError(
                        "The provided timestamp '{}' is invalid.".format(timestamp)
                    )

                dt = datetime.fromtimestamp(float(timestamp), tzinfo)

                return cls(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,
                    dt.tzinfo,
                )

            @classmethod
            def utcfromtimestamp(cls, timestamp):
                """Constructs an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object from a timestamp, in UTC time.
                :param timestamp: an ``int`` or ``float`` timestamp, or a ``str`` that converts to either.
                """

                if not util.is_timestamp(timestamp):
                    raise ValueError(
                        "The provided timestamp '{}' is invalid.".format(timestamp)
                    )

                dt = datetime.utcfromtimestamp(float(timestamp))

                return cls(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,
                    dateutil_tz.tzutc(),
                )

            @classmethod
            def fromdatetime(cls, dt, tzinfo=None):
                """ Constructs an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object from a ``datetime`` and
                optional replacement timezone.
                :param dt: the ``datetime``
                :param tzinfo: (optional) A :ref:`timezone expression <tz-expr>`.  Defaults to ``dt``'s
                    timezone, or UTC if naive.
                If you only want to replace the timezone of naive datetimes::
                    >>> dt
                    datetime.datetime(2013, 5, 5, 0, 0, tzinfo=tzutc())
                    >>> Arrow2.Arrow2.fromdatetime(dt, dt.tzinfo or 'US/Pacific')
                    <Arrow2 [2013-05-05T00:00:00+00:00]>
                """

                if tzinfo is None:
                    if dt.tzinfo is None:
                        tzinfo = dateutil_tz.tzutc()
                    else:
                        tzinfo = dt.tzinfo

                return cls(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,
                    tzinfo,
                )

            @classmethod
            def fromdate(cls, date, tzinfo=None):
                """ Constructs an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object from a ``date`` and optional
                replacement timezone.  Time values are set to 0.
                :param date: the ``date``
                :param tzinfo: (optional) A :ref:`timezone expression <tz-expr>`.  Defaults to UTC.
                """

                if tzinfo is None:
                    tzinfo = dateutil_tz.tzutc()

                return cls(date.year, date.month, date.day, tzinfo=tzinfo)

            @classmethod
            def strptime(cls, date_str, fmt, tzinfo=None):
                """ Constructs an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object from a date string and format,
                in the style of ``datetime.strptime``.  Optionally replaces the parsed timezone.
                :param date_str: the date string.
                :param fmt: the format string.
                :param tzinfo: (optional) A :ref:`timezone expression <tz-expr>`.  Defaults to the parsed
                    timezone if ``fmt`` contains a timezone directive, otherwise UTC.
                Usage::
                    >>> Arrow2.Arrow2.strptime('20-01-2019 15:49:10', '%d-%m-%Y %H:%M:%S')
                    <Arrow2 [2019-01-20T15:49:10+00:00]>
                """

                dt = datetime.strptime(date_str, fmt)
                if tzinfo is None:
                    tzinfo = dt.tzinfo

                return cls(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,
                    tzinfo,
                )

            # factories: ranges and spans

            @classmethod
            def range(cls, frame, start, end=None, tz=None, limit=None):
                """ Returns an iterator of :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` objects, representing
                points in time between two inputs.
                :param frame: The timeframe.  Can be any ``datetime`` property (day, hour, minute...).
                :param start: A datetime expression, the start of the range.
                :param end: (optional) A datetime expression, the end of the range.
                :param tz: (optional) A :ref:`timezone expression <tz-expr>`.  Defaults to
                    ``start``'s timezone, or UTC if ``start`` is naive.
                :param limit: (optional) A maximum number of tuples to return.
                **NOTE**: The ``end`` or ``limit`` must be provided.  Call with ``end`` alone to
                return the entire range.  Call with ``limit`` alone to return a maximum # of results from
                the start.  Call with both to cap a range at a maximum # of results.
                **NOTE**: ``tz`` internally **replaces** the timezones of both ``start`` and ``end`` before
                iterating.  As such, either call with naive objects and ``tz``, or aware objects from the
                same timezone and no ``tz``.
                Supported frame values: year, quarter, month, week, day, hour, minute, second.
                Recognized datetime expressions:
                    - An :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object.
                    - A ``datetime`` object.
                Usage::
                    >>> start = datetime(2013, 5, 5, 12, 30)
                    >>> end = datetime(2013, 5, 5, 17, 15)
                    >>> for r in Arrow2.Arrow2.range('hour', start, end):
                    ...     print(repr(r))
                    ...
                    <Arrow2 [2013-05-05T12:30:00+00:00]>
                    <Arrow2 [2013-05-05T13:30:00+00:00]>
                    <Arrow2 [2013-05-05T14:30:00+00:00]>
                    <Arrow2 [2013-05-05T15:30:00+00:00]>
                    <Arrow2 [2013-05-05T16:30:00+00:00]>
                **NOTE**: Unlike Python's ``range``, ``end`` *may* be included in the returned iterator::
                    >>> start = datetime(2013, 5, 5, 12, 30)
                    >>> end = datetime(2013, 5, 5, 13, 30)
                    >>> for r in Arrow2.Arrow2.range('hour', start, end):
                    ...     print(repr(r))
                    ...
                    <Arrow2 [2013-05-05T12:30:00+00:00]>
                    <Arrow2 [2013-05-05T13:30:00+00:00]>
                """

                _, frame_relative, relative_steps = cls._get_frames(frame)

                tzinfo = cls._get_tzinfo(start.tzinfo if tz is None else tz)

                start = cls._get_datetime(start).replace(tzinfo=tzinfo)
                end, limit = cls._get_iteration_params(end, limit)
                end = cls._get_datetime(end).replace(tzinfo=tzinfo)

                current = cls.fromdatetime(start)
                i = 0

                while current <= end and i < limit:
                    i += 1
                    yield current

                    values = [getattr(current, f) for f in cls._ATTRS]
                    current = cls(*values, tzinfo=tzinfo) + relativedelta(
                        **{frame_relative: relative_steps}
                    )

            @classmethod
            def span_range(cls, frame, start, end, tz=None, limit=None, bounds="[)"):
                """ Returns an iterator of tuples, each :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` objects,
                representing a series of timespans between two inputs.
                :param frame: The timeframe.  Can be any ``datetime`` property (day, hour, minute...).
                :param start: A datetime expression, the start of the range.
                :param end: (optional) A datetime expression, the end of the range.
                :param tz: (optional) A :ref:`timezone expression <tz-expr>`.  Defaults to
                    ``start``'s timezone, or UTC if ``start`` is naive.
                :param limit: (optional) A maximum number of tuples to return.
                :param bounds: (optional) a ``str`` of either '()', '(]', '[)', or '[]' that specifies
                    whether to include or exclude the start and end values in each span in the range. '(' excludes
                    the start, '[' includes the start, ')' excludes the end, and ']' includes the end.
                    If the bounds are not specified, the default bound '[)' is used.
                **NOTE**: The ``end`` or ``limit`` must be provided.  Call with ``end`` alone to
                return the entire range.  Call with ``limit`` alone to return a maximum # of results from
                the start.  Call with both to cap a range at a maximum # of results.
                **NOTE**: ``tz`` internally **replaces** the timezones of both ``start`` and ``end`` before
                iterating.  As such, either call with naive objects and ``tz``, or aware objects from the
                same timezone and no ``tz``.
                Supported frame values: year, quarter, month, week, day, hour, minute, second.
                Recognized datetime expressions:
                    - An :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object.
                    - A ``datetime`` object.
                **NOTE**: Unlike Python's ``range``, ``end`` will *always* be included in the returned
                iterator of timespans.
                Usage:
                    >>> start = datetime(2013, 5, 5, 12, 30)
                    >>> end = datetime(2013, 5, 5, 17, 15)
                    >>> for r in Arrow2.Arrow2.span_range('hour', start, end):
                    ...     print(r)
                    ...
                    (<Arrow2 [2013-05-05T12:00:00+00:00]>, <Arrow2 [2013-05-05T12:59:59.999999+00:00]>)
                    (<Arrow2 [2013-05-05T13:00:00+00:00]>, <Arrow2 [2013-05-05T13:59:59.999999+00:00]>)
                    (<Arrow2 [2013-05-05T14:00:00+00:00]>, <Arrow2 [2013-05-05T14:59:59.999999+00:00]>)
                    (<Arrow2 [2013-05-05T15:00:00+00:00]>, <Arrow2 [2013-05-05T15:59:59.999999+00:00]>)
                    (<Arrow2 [2013-05-05T16:00:00+00:00]>, <Arrow2 [2013-05-05T16:59:59.999999+00:00]>)
                    (<Arrow2 [2013-05-05T17:00:00+00:00]>, <Arrow2 [2013-05-05T17:59:59.999999+00:00]>)
                """

                tzinfo = cls._get_tzinfo(start.tzinfo if tz is None else tz)
                start = cls.fromdatetime(start, tzinfo).span(frame)[0]
                _range = cls.range(frame, start, end, tz, limit)
                return (r.span(frame, bounds=bounds) for r in _range)

            @classmethod
            def interval(cls, frame, start, end, interval=1, tz=None, bounds="[)"):
                """ Returns an iterator of tuples, each :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` objects,
                representing a series of intervals between two inputs.
                :param frame: The timeframe.  Can be any ``datetime`` property (day, hour, minute...).
                :param start: A datetime expression, the start of the range.
                :param end: (optional) A datetime expression, the end of the range.
                :param interval: (optional) Time interval for the given time frame.
                :param tz: (optional) A timezone expression.  Defaults to UTC.
                :param bounds: (optional) a ``str`` of either '()', '(]', '[)', or '[]' that specifies
                    whether to include or exclude the start and end values in the intervals. '(' excludes
                    the start, '[' includes the start, ')' excludes the end, and ']' includes the end.
                    If the bounds are not specified, the default bound '[)' is used.
                Supported frame values: year, quarter, month, week, day, hour, minute, second
                Recognized datetime expressions:
                    - An :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object.
                    - A ``datetime`` object.
                Recognized timezone expressions:
                    - A ``tzinfo`` object.
                    - A ``str`` describing a timezone, similar to 'US/Pacific', or 'Europe/Berlin'.
                    - A ``str`` in ISO 8601 style, as in '+07:00'.
                    - A ``str``, one of the following:  'local', 'utc', 'UTC'.
                Usage:
                    >>> start = datetime(2013, 5, 5, 12, 30)
                    >>> end = datetime(2013, 5, 5, 17, 15)
                    >>> for r in Arrow2.Arrow2.interval('hour', start, end, 2):
                    ...     print r
                    ...
                    (<Arrow2 [2013-05-05T12:00:00+00:00]>, <Arrow2 [2013-05-05T13:59:59.999999+00:00]>)
                    (<Arrow2 [2013-05-05T14:00:00+00:00]>, <Arrow2 [2013-05-05T15:59:59.999999+00:00]>)
                    (<Arrow2 [2013-05-05T16:00:00+00:00]>, <Arrow2 [2013-05-05T17:59:59.999999+00:0]>)
                """
                if interval < 1:
                    raise ValueError("interval has to be a positive integer")

                spanRange = iter(cls.span_range(frame, start, end, tz, bounds=bounds))
                while True:
                    try:
                        intvlStart, intvlEnd = next(spanRange)
                        for _ in range(interval - 1):
                            _, intvlEnd = next(spanRange)
                        yield intvlStart, intvlEnd
                    except StopIteration:
                        return

            # representations

            def __repr__(self):
                return "<{} [{}]>".format(self.__class__.__name__, self.__str__())

            def __str__(self):
                return self._datetime.isoformat()

            def __format__(self, formatstr):

                if len(formatstr) > 0:
                    return self.format(formatstr)

                return str(self)

            def __hash__(self):
                return self._datetime.__hash__()

            # attributes & properties

            def __getattr__(self, name):

                if name == "week":
                    return self.isocalendar()[1]

                if name == "quarter":
                    return int((self.month - 1) / self._MONTHS_PER_QUARTER) + 1

                if not name.startswith("_"):
                    value = getattr(self._datetime, name, None)

                    if value is not None:
                        return value

                return object.__getattribute__(self, name)

            @property
            def tzinfo(self):
                """ Gets the ``tzinfo`` of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object.
                Usage::
                    >>> arw=Arrow2.utcnow()
                    >>> arw.tzinfo
                    tzutc()
                """

                return self._datetime.tzinfo

            @tzinfo.setter
            def tzinfo(self, tzinfo):
                """ Sets the ``tzinfo`` of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object. """

                self._datetime = self._datetime.replace(tzinfo=tzinfo)

            @property
            def datetime(self):
                """ Returns a datetime representation of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object.
                Usage::
                    >>> arw=Arrow2.utcnow()
                    >>> arw.datetime
                    datetime.datetime(2019, 1, 24, 16, 35, 27, 276649, tzinfo=tzutc())
                """

                return self._datetime

            @property
            def naive(self):
                """ Returns a naive datetime representation of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>`
                object.
                Usage::
                    >>> nairobi = Arrow2.now('Africa/Nairobi')
                    >>> nairobi
                    <Arrow2 [2019-01-23T19:27:12.297999+03:00]>
                    >>> nairobi.naive
                    datetime.datetime(2019, 1, 23, 19, 27, 12, 297999)
                """

                return self._datetime.replace(tzinfo=None)

            @property
            def timestamp(self):
                """ Returns a timestamp representation of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object, in
                UTC time.
                Usage::
                    >>> Arrow2.utcnow().timestamp
                    1548260567
                """

                return calendar.timegm(self._datetime.utctimetuple())

            @property
            def float_timestamp(self):
                """ Returns a floating-point representation of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>`
                object, in UTC time.
                Usage::
                    >>> Arrow2.utcnow().float_timestamp
                    1548260516.830896
                """

                return self.timestamp + float(self.microsecond) / 1000000

            # mutation and duplication.

            def clone(self):
                """ Returns a new :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object, cloned from the current one.
                Usage:
                    >>> arw = Arrow2.utcnow()
                    >>> cloned = arw.clone()
                """

                return self.fromdatetime(self._datetime)

            def replace(self, **kwargs):
                """ Returns a new :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object with attributes updated
                according to inputs.
                Use property names to set their value absolutely::
                    >>> import Arrow2
                    >>> arw = Arrow2.utcnow()
                    >>> arw
                    <Arrow2 [2013-05-11T22:27:34.787885+00:00]>
                    >>> arw.replace(year=2014, month=6)
                    <Arrow2 [2014-06-11T22:27:34.787885+00:00]>
                You can also replace the timezone without conversion, using a
                :ref:`timezone expression <tz-expr>`::
                    >>> arw.replace(tzinfo=tz.tzlocal())
                    <Arrow2 [2013-05-11T22:27:34.787885-07:00]>
                """

                absolute_kwargs = {}

                for key, value in kwargs.items():

                    if key in self._ATTRS:
                        absolute_kwargs[key] = value
                    elif key in ["week", "quarter"]:
                        raise AttributeError("setting absolute {} is not supported".format(key))
                    elif key != "tzinfo":
                        raise AttributeError('unknown attribute: "{}"'.format(key))

                current = self._datetime.replace(**absolute_kwargs)

                tzinfo = kwargs.get("tzinfo")

                if tzinfo is not None:
                    tzinfo = self._get_tzinfo(tzinfo)
                    current = current.replace(tzinfo=tzinfo)

                return self.fromdatetime(current)

            def shift(self, **kwargs):
                """ Returns a new :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object with attributes updated
                according to inputs.
                Use pluralized property names to relatively shift their current value:
                >>> import Arrow2
                >>> arw = Arrow2.utcnow()
                >>> arw
                <Arrow2 [2013-05-11T22:27:34.787885+00:00]>
                >>> arw.shift(years=1, months=-1)
                <Arrow2 [2014-04-11T22:27:34.787885+00:00]>
                Day-of-the-week relative shifting can use either Python's weekday numbers
                (Monday = 0, Tuesday = 1 .. Sunday = 6) or using dateutil.relativedelta's
                day instances (MO, TU .. SU).  When using weekday numbers, the returned
                date will always be greater than or equal to the starting date.
                Using the above code (which is a Saturday) and asking it to shift to Saturday:
                >>> arw.shift(weekday=5)
                <Arrow2 [2013-05-11T22:27:34.787885+00:00]>
                While asking for a Monday:
                >>> arw.shift(weekday=0)
                <Arrow2 [2013-05-13T22:27:34.787885+00:00]>
                """

                relative_kwargs = {}
                additional_attrs = ["weeks", "quarters", "weekday"]

                for key, value in kwargs.items():

                    if key in self._ATTRS_PLURAL or key in additional_attrs:
                        relative_kwargs[key] = value
                    else:
                        raise AttributeError(
                            "Invalid shift time frame. Please select one of the following: {}.".format(
                                ", ".join(self._ATTRS_PLURAL + additional_attrs)
                            )
                        )

                # core datetime does not support quarters, translate to months.
                relative_kwargs.setdefault("months", 0)
                relative_kwargs["months"] += (
                    relative_kwargs.pop("quarters", 0) * self._MONTHS_PER_QUARTER
                )

                current = self._datetime + relativedelta(**relative_kwargs)

                return self.fromdatetime(current)

            def to(self, tz):
                """ Returns a new :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object, converted
                to the target timezone.
                :param tz: A :ref:`timezone expression <tz-expr>`.
                Usage::
                    >>> utc = Arrow2.utcnow()
                    >>> utc
                    <Arrow2 [2013-05-09T03:49:12.311072+00:00]>
                    >>> utc.to('US/Pacific')
                    <Arrow2 [2013-05-08T20:49:12.311072-07:00]>
                    >>> utc.to(tz.tzlocal())
                    <Arrow2 [2013-05-08T20:49:12.311072-07:00]>
                    >>> utc.to('-07:00')
                    <Arrow2 [2013-05-08T20:49:12.311072-07:00]>
                    >>> utc.to('local')
                    <Arrow2 [2013-05-08T20:49:12.311072-07:00]>
                    >>> utc.to('local').to('utc')
                    <Arrow2 [2013-05-09T03:49:12.311072+00:00]>
                """

                if not isinstance(tz, dt_tzinfo):
                    tz = parser.TzinfoParser.parse(tz)

                dt = self._datetime.astimezone(tz)

                return self.__class__(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,
                    dt.tzinfo,
                )

            @classmethod
            def _validate_bounds(cls, bounds):
                if bounds != "()" and bounds != "(]" and bounds != "[)" and bounds != "[]":
                    raise AttributeError(
                        'Invalid bounds. Please select between "()", "(]", "[)", or "[]".'
                    )

            def span(self, frame, count=1, bounds="[)"):
                """ Returns two new :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` objects, representing the timespan
                of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object in a given timeframe.
                :param frame: the timeframe.  Can be any ``datetime`` property (day, hour, minute...).
                :param count: (optional) the number of frames to span.
                :param bounds: (optional) a ``str`` of either '()', '(]', '[)', or '[]' that specifies
                    whether to include or exclude the start and end values in the span. '(' excludes
                    the start, '[' includes the start, ')' excludes the end, and ']' includes the end.
                    If the bounds are not specified, the default bound '[)' is used.
                Supported frame values: year, quarter, month, week, day, hour, minute, second.
                Usage::
                    >>> Arrow2.utcnow()
                    <Arrow2 [2013-05-09T03:32:36.186203+00:00]>
                    >>> Arrow2.utcnow().span('hour')
                    (<Arrow2 [2013-05-09T03:00:00+00:00]>, <Arrow2 [2013-05-09T03:59:59.999999+00:00]>)
                    >>> Arrow2.utcnow().span('day')
                    (<Arrow2 [2013-05-09T00:00:00+00:00]>, <Arrow2 [2013-05-09T23:59:59.999999+00:00]>)
                    >>> Arrow2.utcnow().span('day', count=2)
                    (<Arrow2 [2013-05-09T00:00:00+00:00]>, <Arrow2 [2013-05-10T23:59:59.999999+00:00]>)
                    >>> Arrow2.utcnow().span('day', bounds='[]')
                    (<Arrow2 [2013-05-09T00:00:00+00:00]>, <Arrow2 [2013-05-10T00:00:00+00:00]>)
                """

                self._validate_bounds(bounds)

                frame_absolute, frame_relative, relative_steps = self._get_frames(frame)

                if frame_absolute == "week":
                    attr = "day"
                elif frame_absolute == "quarter":
                    attr = "month"
                else:
                    attr = frame_absolute

                index = self._ATTRS.index(attr)
                frames = self._ATTRS[: index + 1]

                values = [getattr(self, f) for f in frames]

                for _ in range(3 - len(values)):
                    values.append(1)

                floor = self.__class__(*values, tzinfo=self.tzinfo)

                if frame_absolute == "week":
                    floor = floor + relativedelta(days=-(self.isoweekday() - 1))
                elif frame_absolute == "quarter":
                    floor = floor + relativedelta(months=-((self.month - 1) % 3))

                ceil = floor + relativedelta(**{frame_relative: count * relative_steps})

                if bounds[0] == "(":
                    floor += relativedelta(microseconds=1)

                if bounds[1] == ")":
                    ceil += relativedelta(microseconds=-1)

                return floor, ceil

            def floor(self, frame):
                """ Returns a new :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object, representing the "floor"
                of the timespan of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object in a given timeframe.
                Equivalent to the first element in the 2-tuple returned by
                :func:`span <Arrow2.Arrow2.Arrow2.span>`.
                :param frame: the timeframe.  Can be any ``datetime`` property (day, hour, minute...).
                Usage::
                    >>> Arrow2.utcnow().floor('hour')
                    <Arrow2 [2013-05-09T03:00:00+00:00]>
                """

                return self.span(frame)[0]

            def ceil(self, frame):
                """ Returns a new :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object, representing the "ceiling"
                of the timespan of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object in a given timeframe.
                Equivalent to the second element in the 2-tuple returned by
                :func:`span <Arrow2.Arrow2.Arrow2.span>`.
                :param frame: the timeframe.  Can be any ``datetime`` property (day, hour, minute...).
                Usage::
                    >>> Arrow2.utcnow().ceil('hour')
                    <Arrow2 [2013-05-09T03:59:59.999999+00:00]>
                """

                return self.span(frame)[1]

            # string output and formatting.

            def format(self, fmt="YYYY-MM-DD HH:mm:ssZZ", locale="en_us"):
                """ Returns a string representation of the :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object,
                formatted according to a format string.
                :param fmt: the format string.
                Usage::
                    >>> Arrow2.utcnow().format('YYYY-MM-DD HH:mm:ss ZZ')
                    '2013-05-09 03:56:47 -00:00'
                    >>> Arrow2.utcnow().format('X')
                    '1368071882'
                    >>> Arrow2.utcnow().format('MMMM DD, YYYY')
                    'May 09, 2013'
                    >>> Arrow2.utcnow().format()
                    '2013-05-09 03:56:47 -00:00'
                """

                return formatter.DateTimeFormatter(locale).format(self._datetime, fmt)

            def humanize(
                self, other=None, locale="en_us", only_distance=False, granularity="auto"
            ):
                """ Returns a localized, humanized representation of a relative difference in time.
                :param other: (optional) an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` or ``datetime`` object.
                    Defaults to now in the current :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object's timezone.
                :param locale: (optional) a ``str`` specifying a locale.  Defaults to 'en_us'.
                :param only_distance: (optional) returns only time difference eg: "11 seconds" without "in" or "ago" part.
                :param granularity: (optional) defines the precision of the output. Set it to strings 'second', 'minute',
                                'hour', 'day', 'week', 'month' or 'year' or a list of any combination of these strings
                Usage::
                    >>> earlier = Arrow2.utcnow().shift(hours=-2)
                    >>> earlier.humanize()
                    '2 hours ago'
                    >>> later = earlier.shift(hours=4)
                    >>> later.humanize(earlier)
                    'in 4 hours'
                """

                locale_name = locale
                locale = locales.get_locale(locale)

                if other is None:
                    utc = datetime.utcnow().replace(tzinfo=dateutil_tz.tzutc())
                    dt = utc.astimezone(self._datetime.tzinfo)

                elif isinstance(other, Arrow2):
                    dt = other._datetime

                elif isinstance(other, datetime):
                    if other.tzinfo is None:
                        dt = other.replace(tzinfo=self._datetime.tzinfo)
                    else:
                        dt = other.astimezone(self._datetime.tzinfo)

                else:
                    raise TypeError(
                        "Invalid 'other' argument of type '{}'. "
                        "Argument must be of type None, Arrow2, or datetime.".format(
                            type(other).__name__
                        )
                    )

                if isinstance(granularity, list) and len(granularity) == 1:
                    granularity = granularity[0]

                delta = int(round(util.total_seconds(self._datetime - dt)))
                sign = -1 if delta < 0 else 1
                diff = abs(delta)
                delta = diff

                try:
                    if granularity == "auto":
                        if diff < 10:
                            return locale.describe("now", only_distance=only_distance)

                        if diff < 45:
                            seconds = sign * delta
                            return locale.describe(
                                "seconds", seconds, only_distance=only_distance
                            )

                        elif diff < 90:
                            return locale.describe("minute", sign, only_distance=only_distance)
                        elif diff < 2700:
                            minutes = sign * int(max(delta / 60, 2))
                            return locale.describe(
                                "minutes", minutes, only_distance=only_distance
                            )

                        elif diff < 5400:
                            return locale.describe("hour", sign, only_distance=only_distance)
                        elif diff < 79200:
                            hours = sign * int(max(delta / 3600, 2))
                            return locale.describe("hours", hours, only_distance=only_distance)

                        # anything less than 48 hours should be 1 day
                        elif diff < 172800:
                            return locale.describe("day", sign, only_distance=only_distance)
                        elif diff < 554400:
                            days = sign * int(max(delta / 86400, 2))
                            return locale.describe("days", days, only_distance=only_distance)

                        elif diff < 907200:
                            return locale.describe("week", sign, only_distance=only_distance)
                        elif diff < 2419200:
                            weeks = sign * int(max(delta / 604800, 2))
                            return locale.describe("weeks", weeks, only_distance=only_distance)

                        elif diff < 3888000:
                            return locale.describe("month", sign, only_distance=only_distance)
                        elif diff < 29808000:
                            self_months = self._datetime.year * 12 + self._datetime.month
                            other_months = dt.year * 12 + dt.month

                            months = sign * int(max(abs(other_months - self_months), 2))

                            return locale.describe(
                                "months", months, only_distance=only_distance
                            )

                        elif diff < 47260800:
                            return locale.describe("year", sign, only_distance=only_distance)
                        else:
                            years = sign * int(max(delta / 31536000, 2))
                            return locale.describe("years", years, only_distance=only_distance)

                    elif util.isstr(granularity):
                        if granularity == "second":
                            delta = sign * delta
                            if abs(delta) < 2:
                                return locale.describe("now", only_distance=only_distance)
                        elif granularity == "minute":
                            delta = sign * delta / self._SECS_PER_MINUTE
                        elif granularity == "hour":
                            delta = sign * delta / self._SECS_PER_HOUR
                        elif granularity == "day":
                            delta = sign * delta / self._SECS_PER_DAY
                        elif granularity == "week":
                            delta = sign * delta / self._SECS_PER_WEEK
                        elif granularity == "month":
                            delta = sign * delta / self._SECS_PER_MONTH
                        elif granularity == "year":
                            delta = sign * delta / self._SECS_PER_YEAR
                        else:
                            raise AttributeError(
                                "Invalid level of granularity. Please select between 'second', 'minute', 'hour', 'day', 'week', 'month' or 'year'"
                            )

                        if trunc(abs(delta)) != 1:
                            granularity += "s"
                        return locale.describe(granularity, delta, only_distance=only_distance)

                    else:
                        timeframes = []
                        if "year" in granularity:
                            years = sign * delta / self._SECS_PER_YEAR
                            delta %= self._SECS_PER_YEAR
                            timeframes.append(["year", years])

                        if "month" in granularity:
                            months = sign * delta / self._SECS_PER_MONTH
                            delta %= self._SECS_PER_MONTH
                            timeframes.append(["month", months])

                        if "week" in granularity:
                            weeks = sign * delta / self._SECS_PER_WEEK
                            delta %= self._SECS_PER_WEEK
                            timeframes.append(["week", weeks])

                        if "day" in granularity:
                            days = sign * delta / self._SECS_PER_DAY
                            delta %= self._SECS_PER_DAY
                            timeframes.append(["day", days])

                        if "hour" in granularity:
                            hours = sign * delta / self._SECS_PER_HOUR
                            delta %= self._SECS_PER_HOUR
                            timeframes.append(["hour", hours])

                        if "minute" in granularity:
                            minutes = sign * delta / self._SECS_PER_MINUTE
                            delta %= self._SECS_PER_MINUTE
                            timeframes.append(["minute", minutes])

                        if "second" in granularity:
                            seconds = sign * delta
                            timeframes.append(["second", seconds])

                        if len(timeframes) < len(granularity):
                            raise AttributeError(
                                "Invalid level of granularity. "
                                "Please select between 'second', 'minute', 'hour', 'day', 'week', 'month' or 'year'."
                            )

                        for tf in timeframes:
                            # Make granularity plural if the delta is not equal to 1
                            if trunc(abs(tf[1])) != 1:
                                tf[0] += "s"
                        return locale.describe_multi(timeframes, only_distance=only_distance)

                except KeyError as e:
                    raise ValueError(
                        "Humanization of the {} granularity is not currently translated in the '{}' locale. "
                        "Please consider making a contribution to this locale.".format(
                            e, locale_name
                        )
                    )

            # query functions

            def is_between(self, start, end, bounds="()"):
                """ Returns a boolean denoting whether the specified date and time is between
                the start and end dates and times.
                :param start: an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object.
                :param end: an :class:`Arrow2 <Arrow2.Arrow2.Arrow2>` object.
                :param bounds: (optional) a ``str`` of either '()', '(]', '[)', or '[]' that specifies
                    whether to include or exclude the start and end values in the range. '(' excludes
                    the start, '[' includes the start, ')' excludes the end, and ']' includes the end.
                    If the bounds are not specified, the default bound '()' is used.
                Usage::
                    >>> start = Arrow2.get(datetime(2013, 5, 5, 12, 30, 10))
                    >>> end = Arrow2.get(datetime(2013, 5, 5, 12, 30, 36))
                    >>> Arrow2.get(datetime(2013, 5, 5, 12, 30, 27)).is_between(start, end)
                    True
                    >>> start = Arrow2.get(datetime(2013, 5, 5))
                    >>> end = Arrow2.get(datetime(2013, 5, 8))
                    >>> Arrow2.get(datetime(2013, 5, 8)).is_between(start, end, '[]')
                    True
                    >>> start = Arrow2.get(datetime(2013, 5, 5))
                    >>> end = Arrow2.get(datetime(2013, 5, 8))
                    >>> Arrow2.get(datetime(2013, 5, 8)).is_between(start, end, '[)')
                    False
                """

                self._validate_bounds(bounds)

                if not isinstance(start, Arrow2):
                    raise TypeError(
                        "Can't parse start date argument type of '{}'".format(type(start))
                    )

                if not isinstance(end, Arrow2):
                    raise TypeError(
                        "Can't parse end date argument type of '{}'".format(type(end))
                    )

                include_start = bounds[0] == "["
                include_end = bounds[1] == "]"

                target_timestamp = self.float_timestamp
                start_timestamp = start.float_timestamp
                end_timestamp = end.float_timestamp

                if include_start and include_end:
                    return (
                        target_timestamp >= start_timestamp
                        and target_timestamp <= end_timestamp
                    )
                elif include_start and not include_end:
                    return (
                        target_timestamp >= start_timestamp and target_timestamp < end_timestamp
                    )
                elif not include_start and include_end:
                    return (
                        target_timestamp > start_timestamp and target_timestamp <= end_timestamp
                    )
                else:
                    return (
                        target_timestamp > start_timestamp and target_timestamp < end_timestamp
                    )

            # math

            def __add__(self, other):

                if isinstance(other, (timedelta, relativedelta)):
                    return self.fromdatetime(self._datetime + other, self._datetime.tzinfo)

                return NotImplemented

            def __radd__(self, other):
                return self.__add__(other)

            def __sub__(self, other):

                if isinstance(other, (timedelta, relativedelta)):
                    return self.fromdatetime(self._datetime - other, self._datetime.tzinfo)

                elif isinstance(other, datetime):
                    return self._datetime - other

                elif isinstance(other, Arrow2):
                    return self._datetime - other._datetime

                return NotImplemented

            def __rsub__(self, other):

                if isinstance(other, datetime):
                    return other - self._datetime

                return NotImplemented

            # comparisons

            def __eq__(self, other):

                if not isinstance(other, (Arrow2, datetime)):
                    return False

                return self._datetime == self._get_datetime(other)

            def __ne__(self, other):

                if not isinstance(other, (Arrow2, datetime)):
                    return True

                return not self.__eq__(other)

            def __gt__(self, other):

                if not isinstance(other, (Arrow2, datetime)):
                    return NotImplemented

                return self._datetime > self._get_datetime(other)

            def __ge__(self, other):

                if not isinstance(other, (Arrow2, datetime)):
                    return NotImplemented

                return self._datetime >= self._get_datetime(other)

            def __lt__(self, other):

                if not isinstance(other, (Arrow2, datetime)):
                    return NotImplemented

                return self._datetime < self._get_datetime(other)

            def __le__(self, other):

                if not isinstance(other, (Arrow2, datetime)):
                    return NotImplemented

                return self._datetime <= self._get_datetime(other)

            def __cmp__(self, other):
                if sys.version_info[0] < 3:  # pragma: no cover
                    if not isinstance(other, (Arrow2, datetime)):
                        raise TypeError(
                            "can't compare '{}' to '{}'".format(type(self), type(other))
                        )

            # datetime methods

            def date(self):
                """ Returns a ``date`` object with the same year, month and day.
                Usage::
                    >>> Arrow2.utcnow().date()
                    datetime.date(2019, 1, 23)
                """

                return self._datetime.date()

            def time(self):
                """ Returns a ``time`` object with the same hour, minute, second, microsecond.
                Usage::
                    >>> Arrow2.utcnow().time()
                    datetime.time(12, 15, 34, 68352)
                """

                return self._datetime.time()

            def timetz(self):
                """ Returns a ``time`` object with the same hour, minute, second, microsecond and
                tzinfo.
                Usage::
                    >>> Arrow2.utcnow().timetz()
                    datetime.time(12, 5, 18, 298893, tzinfo=tzutc())
                """

                return self._datetime.timetz()

            def astimezone(self, tz):
                """ Returns a ``datetime`` object, converted to the specified timezone.
                :param tz: a ``tzinfo`` object.
                Usage::
                    >>> pacific=Arrow2.now('US/Pacific')
                    >>> nyc=Arrow2.now('America/New_York').tzinfo
                    >>> pacific.astimezone(nyc)
                    datetime.datetime(2019, 1, 20, 10, 24, 22, 328172, tzinfo=tzfile('/usr/share/zoneinfo/America/New_York'))
                """

                return self._datetime.astimezone(tz)

            def utcoffset(self):
                """ Returns a ``timedelta`` object representing the whole number of minutes difference from
                UTC time.
                Usage::
                    >>> Arrow2.now('US/Pacific').utcoffset()
                    datetime.timedelta(-1, 57600)
                """

                return self._datetime.utcoffset()

            def dst(self):
                """ Returns the daylight savings time adjustment.
                Usage::
                    >>> Arrow2.utcnow().dst()
                    datetime.timedelta(0)
                """

                return self._datetime.dst()

            def timetuple(self):
                """ Returns a ``time.struct_time``, in the current timezone.
                Usage::
                    >>> Arrow2.utcnow().timetuple()
                    time.struct_time(tm_year=2019, tm_mon=1, tm_mday=20, tm_hour=15, tm_min=17, tm_sec=8, tm_wday=6, tm_yday=20, tm_isdst=0)
                """

                return self._datetime.timetuple()

            def utctimetuple(self):
                """ Returns a ``time.struct_time``, in UTC time.
                Usage::
                    >>> Arrow2.utcnow().utctimetuple()
                    time.struct_time(tm_year=2019, tm_mon=1, tm_mday=19, tm_hour=21, tm_min=41, tm_sec=7, tm_wday=5, tm_yday=19, tm_isdst=0)
                """

                return self._datetime.utctimetuple()

            def toordinal(self):
                """ Returns the proleptic Gregorian ordinal of the date.
                Usage::
                    >>> Arrow2.utcnow().toordinal()
                    737078
                """

                return self._datetime.toordinal()

            def weekday(self):
                """ Returns the day of the week as an integer (0-6).
                Usage::
                    >>> Arrow2.utcnow().weekday()
                    5
                """

                return self._datetime.weekday()

            def isoweekday(self):
                """ Returns the ISO day of the week as an integer (1-7).
                Usage::
                    >>> Arrow2.utcnow().isoweekday()
                    6
                """

                return self._datetime.isoweekday()

            def isocalendar(self):
                """ Returns a 3-tuple, (ISO year, ISO week number, ISO weekday).
                Usage::
                    >>> Arrow2.utcnow().isocalendar()
                    (2019, 3, 6)
                """

                return self._datetime.isocalendar()

            def isoformat(self, sep="T"):
                """Returns an ISO 8601 formatted representation of the date and time.
                Usage::
                    >>> Arrow2.utcnow().isoformat()
                    '2019-01-19T18:30:52.442118+00:00'
                """

                return self._datetime.isoformat(sep)

            def ctime(self):
                """ Returns a ctime formatted representation of the date and time.
                Usage::
                    >>> Arrow2.utcnow().ctime()
                    'Sat Jan 19 18:26:50 2019'
                """

                return self._datetime.ctime()

            def strftime(self, format):
                """ Formats in the style of ``datetime.strftime``.
                :param format: the format string.
                Usage::
                    >>> Arrow2.utcnow().strftime('%d-%m-%Y %H:%M:%S')
                    '23-01-2019 12:28:17'
                """

                return self._datetime.strftime(format)

            def for_json(self):
                """Serializes for the ``for_json`` protocol of simplejson.
                Usage::
                    >>> Arrow2.utcnow().for_json()
                    '2019-01-19T18:25:36.760079+00:00'
                """

                return self.isoformat()

            # internal tools.

            @staticmethod
            def _get_tzinfo(tz_expr):

                if tz_expr is None:
                    return dateutil_tz.tzutc()
                if isinstance(tz_expr, dt_tzinfo):
                    return tz_expr
                else:
                    try:
                        return parser.TzinfoParser.parse(tz_expr)
                    except parser.ParserError:
                        raise ValueError("'{}' not recognized as a timezone".format(tz_expr))

            @classmethod
            def _get_datetime(cls, expr):
                """Get datetime object for a specified expression."""
                if isinstance(expr, Arrow2):
                    return expr.datetime
                elif isinstance(expr, datetime):
                    return expr
                elif util.is_timestamp(expr):
                    timestamp = float(expr)
                    return cls.utcfromtimestamp(timestamp).datetime
                else:
                    raise ValueError(
                        "'{}' not recognized as a datetime or timestamp.".format(expr)
                    )

            @classmethod
            def _get_frames(cls, name):

                if name in cls._ATTRS:
                    return name, "{}s".format(name), 1
                elif name[-1] == "s" and name[:-1] in cls._ATTRS:
                    return name[:-1], name, 1
                elif name in ["week", "weeks"]:
                    return "week", "weeks", 1
                elif name in ["quarter", "quarters"]:
                    return "quarter", "months", 3

                supported = ", ".join(
                    [
                        "year(s)",
                        "month(s)",
                        "day(s)",
                        "hour(s)",
                        "minute(s)",
                        "second(s)",
                        "microsecond(s)",
                        "week(s)",
                        "quarter(s)",
                    ]
                )
                raise AttributeError(
                    "range/span over frame {} not supported. Supported frames: {}".format(
                        name, supported
                    )
                )

            @classmethod
            def _get_iteration_params(cls, end, limit):

                if end is None:

                    if limit is None:
                        raise ValueError("one of 'end' or 'limit' is required")

                    return cls.max, limit

                else:
                    if limit is None:
                        return end, sys.maxsize
                    return end, limit

        # invoke Arrow2 class to ensure it is not left out by a smart compiler
        def use_arrow():
            utc = Arrow2.utcnow()
            now = Arrow2.now()
            return f'{utc} | {now}'

        # invoke functions from two fairly large libraries
        def pandas_numpy(x):
            data = {}
            for i in range(x):
                data[f'value {i}'] = [x for x in range(10)]
            df = pd.DataFrame (data, columns = list(data.keys()))
            arr = np.array(df)
            flatten = reduce(lambda l1,l2: l1+l2, arr.tolist())
            reduced = reduce(lambda n,m: n+m, flatten)
            return reduced


        # ==============================================================

        #  invoke nested functions from arguments
        if 'invoke_nested' in req_json:
            for invoke in req_json['invoke_nested']:
                invoke['invoke_payload']['parent'] = identifier
                invoke['invoke_payload']['level'] = body[identifier]['level']
                nested_response = invoke_nested_function(
                    function_name=invoke['function_name'],
                    invoke_payload=invoke['invoke_payload'],
                    code=invoke['code']
                )
                # add each nested invocation to response body
                for id in nested_response.keys():
                    body[id] = nested_response[id]

        # =============================================
        #  DIFF FROM GENERIC FUNCTIONS
        def get_function():
            if req_json['run_function'] == 'random':
                return functions[random.randint(0,len(functions)-1)]
            else:
                function_to_find = req_json['run_function']
                for f in functions:
                    if f[0] == function_to_find:
                        return f
            raise Exception('no function-name matching the given input')

        (function_name,fx) = get_function()
        result = fx(req_json['args'])
        body[identifier]['function_argument'] = req_json['args']
        body[identifier]['seed'] = req_json['seed']
        body[identifier]['function_called'] = function_name
        body[identifier]['monolith_result'] = str(result)[0:100] if len(str(result)) > 100 else str(result)

        # =============================================

        # add timings and return
        body[identifier]['execution_start'] = start_time
        body[identifier]['execution_end'] = time.time()
        body[identifier]['cpu'] = platform.processor()
        body[identifier]['process_time'] = time.process_time()

        # for azure functions we have to follow the response form
        # that azure provides, so we add an extra key to body that
        # contains the function identifier
        body['identifier'] = identifier

        # set the response status code
        status_code = 200

        # set the response headers
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }

        # create the azure functions response
        response = func.HttpResponse(body=json.dumps(body),
                                     status_code=status_code,
                                     headers=headers,
                                     charset='utf-8'
                                     )

        # return the HTTPResponse
        return response
    # return httpResponse with error if exception occurs
    except Exception as e:
        error_body = {
            "identifier": identifier,
            identifier: {
                "identifier": identifier,
                "uuid": invocation_uuid,
                "function_name": function_name,
                "error": {"trace": traceback.format_exc(), 'message': str(e), "type": str(type(e).__name__)},
                "parent": None,
                "sleep": None,
                "function_cores": psutil.cpu_count(),
                "throughput": None,
                "throughput_time": None,
                "throughput_process_time": None,
                'throughput_running_time': None,
                "random_seed": None,
                "python_version": None,
                "level": None,
                "memory": None,
                "instance_identifier": None,
                "execution_start": start_time,
                "execution_end": time.time(),
                "cpu": platform.processor(),
                "process_time": time.process_time()
            }
        }
        return func.HttpResponse(body=json.dumps(error_body),
                                 status_code=200,
                                 headers={
                                     "Content-Type": "application/json; charset=utf-8"},
                                 charset='utf-8'
                                 )


def invoke_nested_function(function_name: str,
                           invoke_payload: dict,
                           code: str
                           ) -> dict:

    # capture the invocation start time
    start_time = time.time()

    try:
        headers = {
            'Content-Type': 'application/json'
        }

        function_app_name = f'https://{function_name}-python.azurewebsites.net'

        invocation_url = f'{function_app_name}/api/{function_name}?code={code}'

        response = requests.post(
            url=invocation_url,
            headers=headers,
            data=json.dumps(invoke_payload)
        )

        # capture the invocation end time
        end_time = time.time()

        # parse json payload to dict
        body = json.loads(response.content.decode())
        # get identifier of invoked lambda
        id = body['identifier']

        # add invocation start/end times
        body[id]['invocation_start'] = start_time
        body[id]['invocation_end'] = end_time

        return body

    except Exception as e:
        end_time = time.time()
        return {
            "error-"+function_name+'-nested_invocation-'+str(end_time): {
                "identifier": "error-"+function_name+'-nested_invocation-'+str(end_time),
                "uuid": None,
                "function_name": 'function1',
                "error": {"trace": traceback.format_exc(), 'message': str(e), "type": str(type(e).__name__)},
                "parent": invoke_payload['parent'],
                "sleep": None,
                "function_cores": 0,
                "throughput": None,
                "throughput_time": None,
                "throughput_process_time": None,
                'throughput_running_time': None,
                "random_seed": None,
                "python_version": None,
                "level": invoke_payload['level'],
                "memory": None,
                "instance_identifier": None,
                "execution_start": None,
                "execution_end": None,
                "invocation_start": start_time,
                "invocation_end": end_time,
                "cpu": platform.processor(),
                "process_time": time.process_time()
            }
        }


class StatusCodeException(Exception):
    pass
