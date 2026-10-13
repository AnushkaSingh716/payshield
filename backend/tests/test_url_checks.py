from app.services import url_checks


def test_ip_link_is_flagged():
    urls, score, reasons = url_checks.check_urls("Hey, check this out http://203.0.113.7/photos")
    assert urls == ["http://203.0.113.7/photos"]
    assert score >= 40
    assert any("IP address" in r for r in reasons)


def test_shortened_link_is_flagged():
    urls, score, reasons = url_checks.check_urls("Claim here bit.ly/abc123")
    assert urls == ["bit.ly/abc123"]
    assert any("Shortened" in r for r in reasons)


def test_lookalike_bank_domain_is_flagged():
    _, score, reasons = url_checks.check_urls("Visit https://hdfc-kyc-update.xyz/a1b2c now")
    assert score > 40
    assert any("Look-alike" in r for r in reasons)


def test_normal_link_scores_zero():
    urls, score, reasons = url_checks.check_urls("Track at https://www.amazon.in/orders")
    assert urls == ["https://www.amazon.in/orders"]
    assert score == 0
    assert reasons == []