# Merge Marshal

GitHub PR Merge Reminder

`Merge Marshal` is a project for `GitHub` to notify users via direct message (DM) on `Slack` for approved but unmerged
PRs.

Currently, on GitHub integration settings, you can only notify users via public/private `#channel`, not individually.

## Dependencies

- Python 3.11
- slack-sdk 3.33.1
- PyYAML 6.0.2
- aiohttp 3.10.9

## Usage

You need:

- `GitHub` username to `Slack` email address mapping file (author mapping)
- A `GitHub`
  token ([more info](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)).
- A `Slack` token ([more info](https://api.slack.com/authentication/token-types)).

You can run a Docker container with the existing image on Docker Hub:

```sh
docker run -v ./author_mapping.yml:/config/author_mapping.yml \
           -e SLACK_TOKEN=your_slack_token \
           -e GITHUB_TOKEN=your_github_token \
           -e GITHUB_ORGANIZATION_NAME=your_github_token \
           -e DEFAULT_SLACK_EMAIL=your_default_email \
           hadican/merge-marshal:latest
```

### Author Mapping

You need to provide an `author_mapping.yml` file located in the `/config` directory which matches GitHub usernames to
Slack email addresses. If no match is found, then `DEFAULT_SLACK_EMAIL` is notified.

### Environment Variables

You need to set the following environment variables:

- `SLACK_TOKEN`: This is your Slack token, which you can obtain [here](https://api.slack.com/authentication/basics).
- `DEFAULT_SLACK_EMAIL`: This is the default email address to be notified when the author cannot be identified.
- `GITHUB_TOKEN`: This is your GitHub token, which you can obtain [here](https://github.com/settings/tokens).
- `GITHUB_ORGANIZATION_NAME`: This is your GitHub organization name.

### Build Your Own Image

Your Dockerfile is set to run the app. Here's a basic idea of the Docker commands:

To build the Docker image:

```sh
docker build -t merge-marshal .
```

To run the Docker container:

```sh
docker run -v ./author_mapping.yml:/config/author_mapping.yml \
           -e SLACK_TOKEN=your_slack_token \
           -e DEFAULT_SLACK_EMAIL=your_default_email \
           -e GITHUB_TOKEN=your_github_token \
           -e GITHUB_ORGANIZATION_NAME=your_github_token \
           merge-marshal
```