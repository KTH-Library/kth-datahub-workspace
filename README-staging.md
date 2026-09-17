# The staging version of the Datahub Workspace

Is hosted on cbhcloud (kthcloud) by packaging the built site files as a Docker
container and pushing it to cbhcloud (tahaa@kth.se).

The Docker container includes a bare-bones NGINX server configured with
basic authentication (username/password shared among the research data team).

I have configured a CNAME record `workspace.datahub.kth.chepec.se` in the cbhcloud
web admin interface.

To publish the staging site run the `build-staging.sh` script.


## This repo hosts the research data team "support backlog"

This repo ([kth-staging-workspace](https://github.com/KTH-Library/kth-staging-workspace))
hosts the Research data team's internal backlog in the form of a Github project.

+ Any issues created on the `kth-staging-workspace` issue tracker will automatically
  be attached to the backlog project (this was configured by enabling
  the ["Workflow" called "Auto-add to project"](https://github.com/orgs/KTH-Library/projects/10/workflows/99677073)).

You can create new issues for the backlog project in three ways, from either
the project's landing page (in two ways) or from the repo's issue page:

+ from [the project page](https://github.com/orgs/KTH-Library/projects/10),
  click the Plus sign, select "New issue". In the overlay lightbox, ensure
  the header says **Create new issue in KTH-Library/kth-staging-workspace**.
  If it doesn't, click on the left arrow next to it, and use the "Repository"
  drop-down (it's actually a search box) to select/type that repository name.
  Your new issue will then be automatically added to "Todo" in the project
  thanks to the "auto-add" automation configured previously.
+ from the project page, add a new row, i.e., issue, to any of the
  sections ("Todo", "In progress", etc.) by clicking the Plus sign below
  the last row. In this case it seems the issue is always created in the
  correct repo by default!
+ from the [repo's issue page](https://github.com/KTH-Library/kth-staging-workspace/issues),
  create a new issue as usual. It will automatically be added to "Todo" in the
  project.

Note that the repository setting in the project page's "New issue" flow appears
to be non-sticky, meaning you might have to reset it each time. Quite annoying
and [a known problem](https://github.com/orgs/community/discussions/111387)
that Github has apparently [neglected to acknowledge](https://github.com/orgs/community/discussions/186293).



## Links and notes

### Setting the .htpasswd file

The `.htpasswd` file contains just a single username/password, which I created interactively:
```
htpasswd -c .htpasswd kthb
```

This basic auth by a shared username/password is good enough for now.

In the near future, we may use kthcloud's Private Auth proxy instead.
Their Auth Proxy is built on Keycloak, and the developers have indicated to me
that it could be tweaked to allow either *any* authenticated user or a predefined
list of KTH accounts.


### Which Markdown generator is MkDocs using?

> The application uses the **Python-Markdown** Markdown processor.
> You can enable additional extensions.
> https://www.markdownguide.org/tools/mkdocs


#### Python-Markdown

+ https://python-markdown.github.io

> [Python-Markdown] is not a CommonMark implementation; nor is it trying to be!
> Python-Markdown was developed long before the CommonMark specification was
> released and has always (mostly) followed the syntax rules and behavior of
> the original reference implementation. No accommodations have been made to
> address the changes which CommonMark has suggested. It is recommended that
> you look elsewhere if you want an implementation which follows the CommonMark specification.

+ https://python-markdown.github.io/extensions - list of official extensions.
  Although I am not yet sure how to enable an extension for use with MkDocs.

In any case, I cannot find any mention that it supports **caption** or **cross-reference**.
Too bad.
