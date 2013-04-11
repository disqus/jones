import difflib
import json
import logging
import string
import textwrap
from logging.config import dictConfig
from sys import maxint as MAXINT

#TODO: refactor the diffing mail handler into a lib
css = """
    /* for code formatting */
    .codehilite .hll { background-color: #ffffcc }
    .codehilite .c { color: #999988; font-style: italic } /* Comment */
    .codehilite .err { color: #a61717; background-color: #e3d2d2 } /* Error */
    .codehilite .k { color: #000000; font-weight: bold } /* Keyword */
    .codehilite .o { color: #000000; font-weight: bold } /* Operator */
    .codehilite .cm { color: #999988; font-style: italic } /* Comment.Multiline */
    .codehilite .cp { color: #999999; font-weight: bold; font-style: italic } /* Comment.Preproc */
    .codehilite .c1 { color: #999988; font-style: italic } /* Comment.Single */
    .codehilite .cs { color: #999999; font-weight: bold; font-style: italic } /* Comment.Special */
    .codehilite .gd { color: #000000; background-color: #ffdddd } /* Generic.Deleted */
    .codehilite .ge { color: #000000; font-style: italic } /* Generic.Emph */
    .codehilite .gr { color: #aa0000 } /* Generic.Error */
    .codehilite .gh { color: #999999 } /* Generic.Heading */
    .codehilite .gi { color: #000000; background-color: #ddffdd } /* Generic.Inserted */
    .codehilite .go { color: #888888 } /* Generic.Output */
    .codehilite .gp { color: #555555 } /* Generic.Prompt */
    .codehilite .gs { font-weight: bold } /* Generic.Strong */
    .codehilite .gu { color: #aaaaaa } /* Generic.Subheading */
    .codehilite .gt { color: #aa0000 } /* Generic.Traceback */
    .codehilite .kc { color: #000000; font-weight: bold } /* Keyword.Constant */
    .codehilite .kd { color: #000000; font-weight: bold } /* Keyword.Declaration */
    .codehilite .kn { color: #000000; font-weight: bold } /* Keyword.Namespace */
    .codehilite .kp { color: #000000; font-weight: bold } /* Keyword.Pseudo */
    .codehilite .kr { color: #000000; font-weight: bold } /* Keyword.Reserved */
    .codehilite .kt { color: #445588; font-weight: bold } /* Keyword.Type */
    .codehilite .m { color: #009999 } /* Literal.Number */
    .codehilite .s { color: #d01040 } /* Literal.String */
    .codehilite .na { color: #008080 } /* Name.Attribute */
    .codehilite .nb { color: #0086B3 } /* Name.Builtin */
    .codehilite .nc { color: #445588; font-weight: bold } /* Name.Class */
    .codehilite .no { color: #008080 } /* Name.Constant */
    .codehilite .nd { color: #3c5d5d; font-weight: bold } /* Name.Decorator */
    .codehilite .ni { color: #800080 } /* Name.Entity */
    .codehilite .ne { color: #990000; font-weight: bold } /* Name.Exception */
    .codehilite .nf { color: #990000; font-weight: bold } /* Name.Function */
    .codehilite .nl { color: #990000; font-weight: bold } /* Name.Label */
    .codehilite .nn { color: #555555 } /* Name.Namespace */
    .codehilite .nt { color: #000080 } /* Name.Tag */
    .codehilite .nv { color: #008080 } /* Name.Variable */
    .codehilite .ow { color: #000000; font-weight: bold } /* Operator.Word */
    .codehilite .w { color: #bbbbbb } /* Text.Whitespace */
    .codehilite .mf { color: #009999 } /* Literal.Number.Float */
    .codehilite .mh { color: #009999 } /* Literal.Number.Hex */
    .codehilite .mi { color: #009999 } /* Literal.Number.Integer */
    .codehilite .mo { color: #009999 } /* Literal.Number.Oct */
    .codehilite .sb { color: #d01040 } /* Literal.String.Backtick */
    .codehilite .sc { color: #d01040 } /* Literal.String.Char */
    .codehilite .sd { color: #d01040 } /* Literal.String.Doc */
    .codehilite .s2 { color: #d01040 } /* Literal.String.Double */
    .codehilite .se { color: #d01040 } /* Literal.String.Escape */
    .codehilite .sh { color: #d01040 } /* Literal.String.Heredoc */
    .codehilite .si { color: #d01040 } /* Literal.String.Interpol */
    .codehilite .sx { color: #d01040 } /* Literal.String.Other */
    .codehilite .sr { color: #009926 } /* Literal.String.Regex */
    .codehilite .s1 { color: #d01040 } /* Literal.String.Single */
    .codehilite .ss { color: #990073 } /* Literal.String.Symbol */
    .codehilite .bp { color: #999999 } /* Name.Builtin.Pseudo */
    .codehilite .vc { color: #008080 } /* Name.Variable.Class */
    .codehilite .vg { color: #008080 } /* Name.Variable.Global */
    .codehilite .vi { color: #008080 } /* Name.Variable.Instance */
    .codehilite .il { color: #009999 } /* Literal.Number.Integer.Long */

    /* for markdown formatting */
    body{font-family:Helvetica,arial,sans-serif;font-size:14px;line-height:1.6;padding-top:10px;padding-bottom:10px;background-color:white;padding:30px}
    body>*:first-child{margin-top:0!important}body>*:last-child{margin-bottom:0!important}
    a{color:#4183c4}a.absent{color:#c00}a.anchor{display:block;padding-left:30px;margin-left:-30px;cursor:pointer;position:absolute;top:0;left:0;bottom:0}
    h1,h2,h3,h4,h5,h6{margin:20px 0 10px;padding:0;font-weight:bold;-webkit-font-smoothing:antialiased;cursor:text;position:relative}
    h1:hover a.anchor,h2:hover a.anchor,h3:hover a.anchor,h4:hover a.anchor,h5:hover a.anchor,h6:hover a.anchor{background:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA09pVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoMTMuMCAyMDEyMDMwNS5tLjQxNSAyMDEyLzAzLzA1OjIxOjAwOjAwKSAgKE1hY2ludG9zaCkiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6OUM2NjlDQjI4ODBGMTFFMTg1ODlEODNERDJBRjUwQTQiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6OUM2NjlDQjM4ODBGMTFFMTg1ODlEODNERDJBRjUwQTQiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo5QzY2OUNCMDg4MEYxMUUxODU4OUQ4M0REMkFGNTBBNCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo5QzY2OUNCMTg4MEYxMUUxODU4OUQ4M0REMkFGNTBBNCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PsQhXeAAAABfSURBVHjaYvz//z8DJYCRUgMYQAbAMBQIAvEqkBQWXI6sHqwHiwG70TTBxGaiWwjCTGgOUgJiF1J8wMRAIUA34B4Q76HUBelAfJYSA0CuMIEaRP8wGIkGMA54bgQIMACAmkXJi0hKJQAAAABJRU5ErkJggg==) no-repeat 10px center;text-decoration:none}
    h1 tt,h1 code{font-size:inherit}h2 tt,h2 code{font-size:inherit}h3 tt,h3 code{font-size:inherit}
    h4 tt,h4 code{font-size:inherit}h5 tt,h5 code{font-size:inherit}h6 tt,h6 code{font-size:inherit}
    h1{font-size:28px;color:black}h2{font-size:24px;border-bottom:1px solid #ccc;color:black}
    h3{font-size:18px}h4{font-size:16px}h5{font-size:14px}h6{color:#777;font-size:14px}
    p,blockquote,ul,ol,dl,li,table,pre{margin:15px 0}hr{background:transparent url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAYAAAAECAYAAACtBE5DAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYwIDYxLjEzNDc3NywgMjAxMC8wMi8xMi0xNzozMjowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNSBNYWNpbnRvc2giIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6OENDRjNBN0E2NTZBMTFFMEI3QjRBODM4NzJDMjlGNDgiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6OENDRjNBN0I2NTZBMTFFMEI3QjRBODM4NzJDMjlGNDgiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo4Q0NGM0E3ODY1NkExMUUwQjdCNEE4Mzg3MkMyOUY0OCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo4Q0NGM0E3OTY1NkExMUUwQjdCNEE4Mzg3MkMyOUY0OCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PqqezsUAAAAfSURBVHjaYmRABcYwBiM2QSA4y4hNEKYDQxAEAAIMAHNGAzhkPOlYAAAAAElFTkSuQmCC) repeat-x 0 0;border:0 none;color:#ccc;height:4px;padding:0}
    body>h2:first-child{margin-top:0;padding-top:0}body>h1:first-child{margin-top:0;padding-top:0}
    body>h1:first-child+h2{margin-top:0;padding-top:0}body>h3:first-child,body>h4:first-child,body>h5:first-child,body>h6:first-child{margin-top:0;padding-top:0}
    a:first-child h1,a:first-child h2,a:first-child h3,a:first-child h4,a:first-child h5,a:first-child h6{margin-top:0;padding-top:0}
    h1 p,h2 p,h3 p,h4 p,h5 p,h6 p{margin-top:0}li p.first{display:inline-block}li{margin:0}
    ul,ol{padding-left:30px}ul :first-child,ol :first-child{margin-top:0}dl{padding:0}
    dl dt{font-size:14px;font-weight:bold;font-style:italic;padding:0;margin:15px 0 5px}
    dl dt:first-child{padding:0}dl dt>:first-child{margin-top:0}dl dt>:last-child{margin-bottom:0}
    dl dd{margin:0 0 15px;padding:0 15px}dl dd>:first-child{margin-top:0}dl dd>:last-child{margin-bottom:0}
    blockquote{border-left:4px solid #ddd;padding:0 15px;color:#777}blockquote>:first-child{margin-top:0}
    blockquote>:last-child{margin-bottom:0}table{padding:0;border-collapse:collapse}
    table tr{border-top:1px solid #ccc;background-color:white;margin:0;padding:0}table tr:nth-child(2n){background-color:#f8f8f8}
    table tr th{font-weight:bold;border:1px solid #ccc;margin:0;padding:6px 13px}table tr td{border:1px solid #ccc;margin:0;padding:6px 13px}
    table tr th :first-child,table tr td :first-child{margin-top:0}table tr th :last-child,table tr td :last-child{margin-bottom:0}
    img{max-width:100%}span.frame{display:block;overflow:hidden}span.frame>span{border:1px solid #ddd;display:block;float:left;overflow:hidden;margin:13px 0 0;padding:7px;width:auto}
    span.frame span img{display:block;float:left}span.frame span span{clear:both;color:#333;display:block;padding:5px 0 0}
    span.align-center{display:block;overflow:hidden;clear:both}span.align-center>span{display:block;overflow:hidden;margin:13px auto 0;text-align:center}
    span.align-center span img{margin:0 auto;text-align:center}span.align-right{display:block;overflow:hidden;clear:both}
    span.align-right>span{display:block;overflow:hidden;margin:13px 0 0;text-align:right}
    span.align-right span img{margin:0;text-align:right}span.float-left{display:block;margin-right:13px;overflow:hidden;float:left}
    span.float-left span{margin:13px 0 0}span.float-right{display:block;margin-left:13px;overflow:hidden;float:right}
    span.float-right>span{display:block;overflow:hidden;margin:13px auto 0;text-align:right}
    code,tt{margin:0 2px;padding:0 5px;white-space:nowrap;border:1px solid #eaeaea;background-color:#f8f8f8;border-radius:3px}
    pre code{margin:0;padding:0;white-space:pre;border:0;background:transparent}.highlight pre{background-color:#f8f8f8;border:1px solid #ccc;font-size:13px;line-height:19px;overflow:auto;padding:6px 10px;border-radius:3px}
    pre{background-color:#f8f8f8;border:1px solid #ccc;font-size:13px;line-height:19px;overflow:auto;padding:6px 10px;border-radius:3px}
    pre code,pre tt{background-color:transparent;border:0}sup{font-size:.83em;vertical-align:super;line-height:0}
    *{-webkit-print-color-adjust:exact}@media screen and (min-width:914px){body{width:854px;margin:0 auto}
    }@media print{table,pre{page-break-inside:avoid}pre{word-wrap:break-word}}
"""

class MailFilter(logging.Filter):
    """
    Logging filter that decides on if an email should be sent.

    Filter looks for the mail attribute on the record object.
    """
    def filter(self, record):
        """
        :param record: a log record.

        :returns bool: True or False based on record.getattr
        """
        return getattr(record, 'notify', False) or getattr(record, 'mail', False)

class MailFormatter(logging.Formatter):
    """
    Formats log messages for sending as an email.

    Includes all attributes added to the record via the extra dict.
    """

    # remove the whitespace to the left
    template = textwrap.dedent(
        """
        # $formatted_msg

        ## Message context:

        $__formatted_message_context__

        ## Program context:

        $__formatted_program_context__

        """[1:]) # trim first newline

    # attributes to ignore in the record object when building the context_block
    default_attrs = set(('args', 'asctime', 'created', 'dict', 'diff',
      'exc_info', 'exc_text', 'filename', 'funcName', 'levelname', 'levelno',
      'lineno', 'mail', 'message', 'module', 'msecs', 'msg', 'name', 'pathname',
      'process', 'processName', 'relativeCreated', 'thread', 'threadName'))

    program_context_attrs = {
        'Time': '%(asctime)s',
        'Message type': '%(levelname)s',
        'Location': '%(pathname)s:%(lineno)s',
        'Module': '%(module)s',
        'Function': '%(funcName)s',
    }

    def coerce_to_splitlines(self, obj):
        """
        :param obj: object to coerce into a list of strings split on newline.
          obj should be either an object that can be serialzed to json or a json
          encoded string

        - If obj is a string `coerce_to_splitlines` will attempt to json decode
          first.
        - If obj is not a string it will be json encoded with indent=2 and then
          json encoded.

        :returns list: a list of strings suitable for use with the difflib functions.
        """

        if isinstance(obj, basestring):
            try:
                obj = json.loads(obj)
            except (TypeError, ValueError):
                raise

        try:
            ret = json.dumps(obj, indent=2, sort_keys=True)
        except (TypeError, ValueError):
            raise
        else:
            return ret.split('\n')

    def diff(self, path, a, b):
        """
        Format a diff of two objects.
        """
        a = self.coerce_to_splitlines(a)
        b = self.coerce_to_splitlines(b)

        diff = difflib.unified_diff(a, b,
            fromfile='before: ' + path,
            tofile='after: ' + path,
            n=MAXINT # lines of context all the things!
            )

        diff_string = ':::diff\n' + '\n'.join(l.rstrip() for l in diff) or "The data is unchanged."

        return diff_string

    def format_context_pair(self, key, value, pad=8):
        """
        :param key: the lvalue of the formatted output
        :param value: the rvalue. If key is not a string it will be displayed as
            'code' in the markdown format.
        """

        key = str(key) + ": "

        dumps = False # set a flag for 'should be code' or not
        if not isinstance(value, basestring):
            value = ":::python\n" + json.dumps(value, indent=2, sort_keys=True)
            dumps = True

        # newline + pad * spaces
        nlsppad = "\n" + " " * pad
        shouldnl = "\n" + nlsppad if len(key) >= pad or dumps else ""

        return "- {1:<{0}}{3}{2}".format(pad, key, value.replace("\n", nlsppad), shouldnl)

    def format(self, record):
        """
        :param record: a log record.

        :returns: The formatted string for the email.
        """
        # build up some of the expected items for formatting
        record.asctime = self.formatTime(record, self.datefmt)

        # for compatability set record.message to support %(message)s
        record.message = record.msg

        ## build a string to include the local context of what changed

        # add a diff section if context is provided
        diffs = dict((path, self.diff(path, *objs)) for path, objs in getattr(record, 'diff', {}).iteritems() if len(objs) == 2)

        # format and join the diffs
        diff_context = [self.format_context_pair(path, diff) for path, diff in sorted(diffs.items())]

        # format and join the extra attrs
        message_context = [self.format_context_pair(attr, value) for attr, value in sorted(record.__dict__.items()) if attr not in self.default_attrs]

        # format and join the program context
        program_context = [self.format_context_pair(title, attr % record.__dict__, pad=16) for title, attr in self.program_context_attrs.iteritems()]

        # add the formatted extras for template formatting
        record.__formatted_message_context__ = '\n\n'.join(diff_context + message_context)
        record.__formatted_program_context__ = '\n'.join(program_context)

        # add a record for a formatted message
        record.formatted_msg = record.msg % record.__dict__

        # perform the template substitution
        ret = string.Template(self.template).safe_substitute(record.__dict__)

        return ret

class MailHandler(logging.handlers.SMTPHandler):
    """
    SMTPHandler that has a custom subject line based on the record.msg attribute.
    """
    def getSubject(self, record):
        """
        :param record: a log record.

        :returns str: formatted subject line based on configured subject and `record`
        """
        # 1) format the subject with the record
        # 2) if the key msg was used, we need to format that as well
        # can't rely on %(formatted_message)s working incase the handler is changed
        return self.subject % record.__dict__ % record.__dict__

    def emit(self, record):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # still work if there is no markdown formatting library
        try:
            from markdown import markdown
        except:
            markdown = None

        # still work if there is no css in lining library
        try:
            from pynliner import Pynliner
        except:
            Pynliner = None

        try:
            from email.utils import formatdate
        except ImportError:
            formatdate = self.date_time

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.getSubject(record)
        msg['From'] = self.fromaddr
        msg['To'] = ",".join(self.toaddrs)
        msg['Date'] = formatdate()

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.

        formatted_msg = self.format(record)
        msg.attach(MIMEText(formatted_msg, 'plain'))

        # these can fail, still want the email though
        try:
            html = markdown(formatted_msg, ['codehilite(linenums=False, noclasses=True)', 'extra'], output_format='html5') if markdown else formatted_msg

            try:
                inline_html = Pynliner().from_string(html).with_cssString(css).run() if Pynliner else html
            except:
                msg.attach(MIMEText(html, 'html'))
            else:
                msg.attach(MIMEText(inline_html, 'html'))
        except:
            pass

        try:
            port = self.mailport or smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            if self.username:
                smtp.login(self.username, self.password)

            smtp.sendmail(self.fromaddr, self.toaddrs, msg.as_string())
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "mail": { "()": MailFormatter, },
    },
    "filters": {
        "mail": { "()": MailFilter, },
    },
    "handlers": {
        "sentry": {
            "level": "ERROR",
            "class": "raven.handlers.logging.SentryHandler",
            "dsn": "http://bc3bbf5629104effb722450ed18c8400:95912a1f566648988b74ccc78fd78fd9@sentry.local.disqus.net/17",
        },
        "mail": {
            "()": MailHandler,
            "level": "INFO",
            "formatter": "mail",
            "filters": ["mail"],
            "mailhost": ("localhost", "587"),
            "fromaddr": "jones@disqus.com",
            "toaddrs": ["team+jones@disqus.com",],
            "subject": "[jones-all] %(msg)s",
            "credentials": ['username', 'password'],
        },
        "console-mail": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "mail",
            "filters": ["mail"],
        },
    },
    "loggers": {
        "": {
            "handlers": [
                "mail", # sends an email for all logs with extra={"mail":True}
                # "console-mail", # sends an email for all logs with extra={"mail":True}
                "sentry", # alert on all error or exceptions
            ],
            "level": "INFO",
        },
    },
}


def configure(extra_config=None):
    """
    Configures logging for the application based on the config.

    :param dict extra_config: options to update the default config with.
    """
    composite_config = {}
    composite_config.update(config)
    if extra_config:
        composite_config.update(extra_config)

    dictConfig(composite_config)
