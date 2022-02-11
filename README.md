# Automatically Create Branch Protection Rules and Issues with GitHub API

The project uses python to listen to organization events, and then proceed to do the following:

1. Check if a repository has been initialized; if not, then add a `Readme.md`
2. Create a branch protection rule on the `default branch`
3. Create an issue in newly created repository, outlining the policies created


### Resources Used

1. [Intro to Webhooks and Python](https://towardsdatascience.com/intro-to-webhooks-and-how-to-receive-them-with-python-d5f6dd634476)
2. [Ngrok for Exposing URLs](https://ngrok.com/docs#getting-started-expose)
3. [Gatsby's Introduction to GraphiQL](https://www.gatsbyjs.com/docs/how-to/querying-data/running-queries-with-graphiql/)