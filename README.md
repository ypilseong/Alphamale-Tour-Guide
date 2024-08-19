# Alphamale Tour Guide

[![pypi-image]][pypi-url]
[![version-image]][release-url]
[![release-date-image]][release-url]
[![license-image]][license-url]
[![codecov][codecov-image]][codecov-url]
[![jupyter-book-image]][docs-url]

<!-- Links: -->
[codecov-image]: https://codecov.io/gh/ypilseong/Alphamale-Tour-Guide/branch/main/graph/badge.svg?token=[REPLACE_ME]
[codecov-url]: https://codecov.io/gh/ypilseong/Alphamale-Tour-Guide
[pypi-image]: https://img.shields.io/pypi/v/alphamale-tour-guide
[license-image]: https://img.shields.io/github/license/ypilseong/Alphamale-Tour-Guide
[license-url]: https://github.com/ypilseong/Alphamale-Tour-Guide/blob/main/LICENSE
[version-image]: https://img.shields.io/github/v/release/ypilseong/Alphamale-Tour-Guide?sort=semver
[release-date-image]: https://img.shields.io/github/release-date/ypilseong/Alphamale-Tour-Guide
[release-url]: https://github.com/ypilseong/Alphamale-Tour-Guide/releases
[jupyter-book-image]: https://jupyterbook.org/en/stable/_images/badge.svg

[repo-url]: https://github.com/ypilseong/Alphamale-Tour-Guide
[pypi-url]: https://pypi.org/project/alphamale-tour-guide
[docs-url]: https://ypilseong.github.io/Alphamale-Tour-Guide
[changelog]: https://github.com/ypilseong/Alphamale-Tour-Guide/blob/main/CHANGELOG.md
[contributing guidelines]: https://github.com/ypilseong/Alphamale-Tour-Guide/blob/main/CONTRIBUTING.md
<!-- Links: -->

## Project Overview

**Alphamale Tour Guide** is an AI-powered chatbot designed to help users plan customized trips to Jeju Island. Due to the overwhelming number of advertisements on social media, finding specific and personalized tourist spots in Jeju can be difficult. This project aims to solve that problem by providing tailored recommendations and planning routes for your itinerary. 

The chatbot leverages Upstage's 'solar-1-mini-chat' API to understand user preferences and recommend attractions accordingly. To enhance the reliability of the recommendations, the chatbot also utilizes data from Korea's Naver search portal to cross-check and refine suggestions.

## Installation

To install and set up the Alphamale Tour Guide, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/ypilseong/Alphamale-Tour-Guide.git
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

After installing the necessary packages, you can start the chatbot by running:

```bash
python3 inference.py
```

### Important Notes

- **Naver API Credentials:** The project requires Naver API keys for accessing the search portal. You can obtain these keys from [Naver Developers](https://developers.naver.com/products/service-api/datalab/datalab.md) for `naver_client_id` and `naver_client_secret`.

- **NCP Client ID:** For route optimization and map features, you'll need an NCP client ID from [Naver Cloud Platform](https://www.ncloud.com/?language=ko-KR).

- The credentials should be added to the following files:
    - `gradio/inference.py`:
    ```python
    upstage_api_key = os.getenv("UPSTAGE_API_KEY")
    naver_client_id = os.getenv("NAVER_CLIENT_ID")
    naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
    ```
    - `route_opt/index.html`:
    ```html
    <script type="text/javascript" src="https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId={key}"></script>
    ```

### Upstage API Integration

The Upstage 'solar-1-mini-chat' API is utilized within the project to handle natural language processing tasks. This API allows the chatbot to comprehend user queries and provide accurate and personalized recommendations based on individual preferences.

### Documentation

Full documentation is available at: [https://ypilseong.github.io/Alphamale-Tour-Guide][docs-url]

### Changelog

See the [CHANGELOG] for detailed updates.

### Contributing

Contributions are welcome! Please see the [contributing guidelines] for more information.

### License

This project is released under the [MIT License][license-url].
