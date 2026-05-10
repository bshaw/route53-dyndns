import sys
from unittest.mock import MagicMock, patch

import pytest

import r53dyndns
from tests.conftest import NEW_IP, OLD_IP, RECORD, ZONE


def test_get_current_ip():
    rdata = MagicMock()
    rdata.__str__ = lambda self: NEW_IP
    with patch('socket.gethostbyname', return_value='208.67.222.222'):
        with patch('dns.resolver.Resolver') as MockResolver:
            MockResolver.return_value.resolve.return_value = [rdata]
            ip = r53dyndns.get_current_ip()
    assert ip == NEW_IP


def test_get_zone(route53, zone_id):
    assert r53dyndns.get_zone(ZONE) == zone_id


def test_get_zone_not_found(route53):
    with pytest.raises(ValueError, match='No hosted zone found'):
        r53dyndns.get_zone('notexist.com')


def test_get_record_ip(seeded_record):
    assert r53dyndns.get_record_ip(seeded_record, RECORD) == OLD_IP


def test_get_record_ip_not_found(route53, zone_id):
    with pytest.raises(ValueError, match='No A record found'):
        r53dyndns.get_record_ip(zone_id, RECORD)


def test_update_record(seeded_record):
    status = r53dyndns.update_record(seeded_record, RECORD, NEW_IP)
    assert status == 'INSYNC'
    assert r53dyndns.get_record_ip(seeded_record, RECORD) == NEW_IP


def test_main_no_update_when_ip_matches(seeded_record, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['r53dyndns.py', '--record', RECORD])
    with patch('r53dyndns.get_current_ip', return_value=OLD_IP):
        with pytest.raises(SystemExit) as exc:
            r53dyndns.main()
    assert exc.value.code == 0


def test_main_updates_record_when_ip_changed(seeded_record, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['r53dyndns.py', '--record', RECORD])
    with patch('r53dyndns.get_current_ip', return_value=NEW_IP):
        r53dyndns.main()
    assert r53dyndns.get_record_ip(seeded_record, RECORD) == NEW_IP
