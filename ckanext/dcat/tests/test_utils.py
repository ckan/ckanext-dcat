import nose

from ckanext.dcat.utils import parse_accept_header

eq_ = nose.tools.eq_


class TestAcceptHeaders(object):

    def test_empty(self):

        header = ''

        _format = parse_accept_header(header)

        eq_(_format, None)

    def test_basic_found(self):

        header = 'application/rdf+xml'

        _format = parse_accept_header(header)

        eq_(_format, 'rdf')

    def test_basic_not_found(self):

        header = 'image/gif'

        _format = parse_accept_header(header)

        eq_(_format, None)

    def test_multiple(self):

        header = 'application/rdf+xml, application/ld+json'

        _format = parse_accept_header(header)

        eq_(_format, 'rdf')

    def test_multiple_not_found(self):

        header = 'image/gif, text/unknown'

        _format = parse_accept_header(header)

        eq_(_format, None)

    def test_multiple_first_not_found(self):

        header = 'image/gif, application/ld+json, text/turtle'

        _format = parse_accept_header(header)

        eq_(_format, 'jsonld')

    def test_q_param(self):

        header = 'text/turtle; q=0.8'

        _format = parse_accept_header(header)

        eq_(_format, 'ttl')

    def test_q_param_multiple(self):

        header = 'text/turtle; q=0.8, text/n3; q=0.6'

        _format = parse_accept_header(header)

        eq_(_format, 'ttl')

    def test_q_param_multiple_first_not_found(self):

        header = 'image/gif; q=1.0, text/turtle; q=0.8, text/n3; q=0.6'

        _format = parse_accept_header(header)

        eq_(_format, 'ttl')

    def test_wildcard(self):

        header = 'text/*'

        _format = parse_accept_header(header)

        assert _format in ('ttl', 'n3')

    def test_wildcard_multiple(self):

        header = 'image/gif; q=1.0, text/*; q=0.5'

        _format = parse_accept_header(header)

        assert _format in ('ttl', 'n3')

    def test_double_wildcard(self):

        header = '*/*'

        _format = parse_accept_header(header)

        eq_(_format, None)

    def test_double_wildcard_multiple(self):

        header = 'image/gif; q=1.0, text/csv; q=0.8, */*; q=0.1'

        _format = parse_accept_header(header)

        eq_(_format, None)

    def test_html(self):

        header = 'text/html'

        _format = parse_accept_header(header)

        eq_(_format, None)

    def test_html_multiple(self):

        header = 'image/gif; q=1.0, text/html; q=0.8, text/turtle; q=0.6'

        _format = parse_accept_header(header)

        eq_(_format, None)
