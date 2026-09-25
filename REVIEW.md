<!-- balka:begin -->
# Review policy

The review passes live in `.github/copilot-instructions.md`, where Copilot code
review applies them to every pull request and `/balka:deploy` addresses what
it finds. Edit them there.

Production releases wait for a named approver. Install that gate with
`/balka:init --gate`.
<!-- balka:end -->
