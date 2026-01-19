import pytest

from url_to_pdf.image_handler import is_ad_url


class TestIsAdUrl:
    def test_regular_image_url(self):
        url = "https://example.com/images/photo.jpg"
        assert is_ad_url(url) is False

    def test_uploads_not_matched(self):
        url = "https://example.com/wp-content/uploads/2024/image.jpg"
        assert is_ad_url(url) is False

    def test_ad_pattern_matched(self):
        url = "https://example.com/ads/banner.jpg"
        assert is_ad_url(url) is True

    def test_banner_matched(self):
        url = "https://example.com/images/banner-top.jpg"
        assert is_ad_url(url) is True

    def test_tracker_matched(self):
        url = "https://example.com/tracker/pixel.gif"
        assert is_ad_url(url) is True

    def test_logo_matched(self):
        url = "https://example.com/logo.png"
        assert is_ad_url(url) is True

    def test_analytics_matched(self):
        url = "https://example.com/analytics/track.gif"
        assert is_ad_url(url) is True

    def test_sber_matched(self):
        url = "https://example.com/images/sber-pay.png"
        assert is_ad_url(url) is True

    def test_yoomoney_matched(self):
        url = "https://example.com/yoomoney-button.png"
        assert is_ad_url(url) is True

    def test_boosty_matched(self):
        url = "https://example.com/boosty-logo.png"
        assert is_ad_url(url) is True

    def test_case_insensitive(self):
        url = "https://example.com/BANNER.jpg"
        assert is_ad_url(url) is True
