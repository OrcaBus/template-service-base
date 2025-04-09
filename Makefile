.PHONY: test deep scan

check:
	@pnpm audit
	@pnpm prettier
	@pnpm eslint
	@pre-commit run --all-files

install:
	@pnpm install --frozen-lockfile

test:
	@pnpm test
