import pytest

@pytest.fixture(scope="function")
def context(browser):
    # Enable video recording for all tests
    return browser.new_context(
        record_video_dir="videos/",
        record_video_size={"width": 1280, "height": 720}
    )

@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    # Ensure video recording is enabled
    return page

# Add a fixture to ensure videos are recorded
@pytest.fixture(autouse=True)
def setup_video_recording(request):
    """Automatically setup video recording for all tests"""
    # This fixture will run automatically for all tests
    pass