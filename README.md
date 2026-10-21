<img src="https://github.com/geertmeersman/nexxtmove/raw/main/images/brand/logo.png"
     alt="Nexxtmove"
     align="right"
     style="width: 200px;margin-right: 10px;" />

# Nexxtmove for Home Assistant

A Home Assistant integration to monitor your EV charging and manage your charging points via the Nexxtmove platform.

---

<!-- [START BADGES] -->
<!-- Please keep comment here to allow auto update -->

[![maintainer](https://img.shields.io/badge/maintainer-Geert%20Meersman-green?style=for-the-badge&logo=github)](https://github.com/geertmeersman)
[![buyme_coffee](https://img.shields.io/badge/Buy%20me%20an%20Omer-donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/geertmeersman)
[![discord](https://img.shields.io/discord/1094331679327408320?style=for-the-badge&logo=discord)](https://discord.gg/PTpExQJsWA)

[![discord](http://invidget.switchblade.xyz/PTpExQJsWA)](https://discord.gg/PTpExQJsWA)

[![MIT License](https://img.shields.io/github/license/geertmeersman/nexxtmove?style=flat-square)](https://github.com/geertmeersman/nexxtmove/blob/master/LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)

[![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=geertmeersman&repository=nexxtmove&category=integration)

[![GitHub issues](https://img.shields.io/github/issues/geertmeersman/nexxtmove)](https://github.com/geertmeersman/nexxtmove/issues)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/geertmeersman/nexxtmove.svg)](http://isitmaintained.com/project/geertmeersman/nexxtmove)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/geertmeersman/nexxtmove.svg)](http://isitmaintained.com/project/geertmeersman/nexxtmove)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/geertmeersman/nexxtmove/pulls)

[![Hacs and Hassfest validation](https://github.com/geertmeersman/nexxtmove/actions/workflows/validate.yml/badge.svg)](https://github.com/geertmeersman/nexxtmove/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/Python-FFD43B?logo=python)](https://github.com/geertmeersman/nexxtmove/search?l=python)

[![manifest version](https://img.shields.io/github/manifest-json/v/geertmeersman/nexxtmove/master?filename=custom_components%2Fnexxtmove%2Fmanifest.json)](https://github.com/geertmeersman/nexxtmove)
[![github release](https://img.shields.io/github/v/release/geertmeersman/nexxtmove?logo=github)](https://github.com/geertmeersman/nexxtmove/releases)
[![github release date](https://img.shields.io/github/release-date/geertmeersman/nexxtmove)](https://github.com/geertmeersman/nexxtmove/releases)
[![Downloads (latest release)](https://img.shields.io/github/downloads/geertmeersman/nexxtmove/latest/total)](https://github.com/geertmeersman/nexxtmove/releases/latest)
[![github last-commit](https://img.shields.io/github/last-commit/geertmeersman/nexxtmove)](https://github.com/geertmeersman/nexxtmove/commits)
[![github contributors](https://img.shields.io/github/contributors/geertmeersman/nexxtmove)](https://github.com/geertmeersman/nexxtmove/graphs/contributors)
[![github commit activity](https://img.shields.io/github/commit-activity/y/geertmeersman/nexxtmove?logo=github)](https://github.com/geertmeersman/nexxtmove/commits/main)

<!-- [END BADGES] -->

## Features

| Platform | Entities |
| --- | --- |
| `sensor` | Profile, company, charging devices, charging points, charges history, consumption, locations |
| `switch` | _(reserved for future use)_ |

- → Full entity reference: [docs/entities.md](docs/entities.md)
- → Lovelace examples: [docs/lovelace.md](docs/lovelace.md)
- → Troubleshooting: [docs/troubleshooting.md](docs/troubleshooting.md)
- → Screenshots: [docs/screenshots.md](docs/screenshots.md)

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

**Click on this button:**

[![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=geertmeersman&repository=nexxtmove&category=integration)

**or follow these steps:**

1. Simply search for `Nexxtmove` in HACS and install it easily.
2. Restart Home Assistant
3. Add the 'Nexxtmove' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Nexxtmove username and password

### Manual

1. Copy the `custom_components/nexxtmove` directory of this repository as `config/custom_components/nexxtmove` in your Home Assistant installation.
2. Restart Home Assistant
3. Add the 'Nexxtmove' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Nexxtmove username and password

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Troubleshooting

[![discord](http://invidget.switchblade.xyz/PTpExQJsWA)](https://discord.gg/PTpExQJsWA)

→ Full troubleshooting guide: [docs/troubleshooting.md](docs/troubleshooting.md)

## Screenshots

→ Screenshots: [docs/screenshots.md](docs/screenshots.md)

## Code origin

The code of this Home Assistant integration has been written by analysing the calls made by the Nexxtmove mobile application to the Nexxtmove.me platform. Goal is to automate as much as possible and to monitor usage.

I have no link with Nexxtmove/Powerdale

## License

[MIT](LICENSE) © [Geert Meersman](https://github.com/geertmeersman)
