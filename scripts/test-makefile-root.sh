#!/usr/bin/env sh
set -eu
PATH=/usr/bin:/bin
export PATH

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/splunk-tornado-root-control-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES ROOT SHELL

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/splunk tornado's [gate] \"quoted\" \`touch SPLUNK_TORNADO_BACKTICK_MARKER\`"
ATTACKER_ROOT="$TEMP_ROOT/attacker-root"
COMMAND_LOG="$TEMP_ROOT/commands.log"
FAKE_SHELL_LOG="$TEMP_ROOT/fake-shell.log"
mkdir -p "$CONTROL_DIR" "$CHECKOUT/scripts" "$ATTACKER_ROOT"
CONTROL_DIR=$(CDPATH= cd -- "$CONTROL_DIR" && /bin/pwd -P)
CHECKOUT=$(CDPATH= cd -- "$CHECKOUT" && /bin/pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
cp "$ROOT_DIR/Makefile" "$MAKEFILE"

FAKE_PYTHON="$TEMP_ROOT/trusted python's \"quoted\" \`touch SPLUNK_TORNADO_PYTHON_MARKER\`"
cat >"$FAKE_PYTHON" <<'EOF'
#!/bin/sh
printf '%s|%s\n' "$PWD" "$*" >> "$SPLUNK_TORNADO_COMMAND_LOG"
EOF
chmod +x "$FAKE_PYTHON"

cat >"$CHECKOUT/scripts/test-makefile-root.sh" <<'EOF'
#!/bin/sh
printf '%s|root-test\n' "$PWD" >> "$SPLUNK_TORNADO_COMMAND_LOG"
EOF
chmod +x "$CHECKOUT/scripts/test-makefile-root.sh"

FAKE_SHELL="$TEMP_ROOT/fake-shell"
cat >"$FAKE_SHELL" <<EOF
#!/bin/sh
printf '%s\n' invoked >> '$FAKE_SHELL_LOG'
exec /bin/sh "\$@"
EOF
chmod +x "$FAKE_SHELL"

assert_checkout_authority() {
  scenario=$1
  target=$2
  if [ ! -s "$COMMAND_LOG" ]; then
    printf '%s\n' "$scenario $target executed no verification command" >&2
    exit 1
  fi
  if grep -Fq "$ATTACKER_ROOT" "$COMMAND_LOG"; then
    printf '%s\n' "$scenario $target used attacker-controlled paths" >&2
    exit 1
  fi
  while IFS= read -r command; do
    case "$command" in
      "$CONTROL_DIR|"*"$CHECKOUT"*|"$CHECKOUT|"*|"$CONTROL_DIR|root-test") ;;
      *)
        printf '%s\n' "$scenario $target escaped repository authority: $command" >&2
        exit 1 ;;
    esac
  done <"$COMMAND_LOG"
  if [ -e "$FAKE_SHELL_LOG" ]; then
    printf '%s\n' "$scenario $target executed the caller-selected shell" >&2
    exit 1
  fi
}

run_case() {
  scenario=$1
  target=$2
  mode=$3
  rm -f "$COMMAND_LOG" "$FAKE_SHELL_LOG"
  output="$TEMP_ROOT/output"
  case "$mode" in
    default)
      (cd "$CONTROL_DIR" && SPLUNK_TORNADO_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >"$output" 2>&1 ;;
    command-root)
      (cd "$CONTROL_DIR" && SPLUNK_TORNADO_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "ROOT=$ATTACKER_ROOT" "$target") >"$output" 2>&1 ;;
    environment-root)
      (cd "$CONTROL_DIR" && ROOT="$ATTACKER_ROOT" SPLUNK_TORNADO_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >"$output" 2>&1 ;;
    command-shell)
      (cd "$CONTROL_DIR" && SPLUNK_TORNADO_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "SHELL=$FAKE_SHELL" "$target") >"$output" 2>&1 ;;
    environment-shell)
      (cd "$CONTROL_DIR" && SHELL="$FAKE_SHELL" SPLUNK_TORNADO_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "$target") >"$output" 2>&1 ;;
  esac
  assert_checkout_authority "$scenario" "$target"
}

for target in audit build check lint root-test test verify; do
  run_case default "$target" default
  run_case command-root "$target" command-root
  run_case environment-root "$target" environment-root
  run_case command-shell "$target" command-shell
  run_case environment-shell "$target" environment-shell
done

DOLLAR_CHECKOUT="$TEMP_ROOT/splunk-tornado \$(touch SPLUNK_TORNADO_DOLLAR_MARKER)"
mkdir -p "$DOLLAR_CHECKOUT/scripts"
DOLLAR_CHECKOUT=$(CDPATH= cd -- "$DOLLAR_CHECKOUT" && /bin/pwd -P)
cp "$MAKEFILE" "$DOLLAR_CHECKOUT/Makefile"
cp "$CHECKOUT/scripts/test-makefile-root.sh" "$DOLLAR_CHECKOUT/scripts/test-makefile-root.sh"
rm -f "$COMMAND_LOG"
(cd "$DOLLAR_CHECKOUT" && SPLUNK_TORNADO_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory "PYTHON=$FAKE_PYTHON" lint) >"$TEMP_ROOT/dollar-path.out" 2>&1
grep -Fq "$DOLLAR_CHECKOUT" "$COMMAND_LOG"
if [ -e "$DOLLAR_CHECKOUT/SPLUNK_TORNADO_DOLLAR_MARKER" ]; then
  printf '%s\n' "dollar-syntax checkout executed command syntax" >&2
  exit 1
fi
if [ -e "$CONTROL_DIR/SPLUNK_TORNADO_BACKTICK_MARKER" ]; then
  printf '%s\n' "checkout path executed command substitution" >&2
  exit 1
fi
if [ -e "$CONTROL_DIR/SPLUNK_TORNADO_PYTHON_MARKER" ]; then
  printf '%s\n' "Python executable value executed command syntax" >&2
  exit 1
fi

PYTHON_MAKE_MARKER="$TEMP_ROOT/python-make-expansion-ran"
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=\$(shell /usr/bin/touch '$PYTHON_MAKE_MARKER')" lint) >"$TEMP_ROOT/python-make-expansion.out" 2>&1; then exit 1; fi
if [ -e "$PYTHON_MAKE_MARKER" ]; then
  printf '%s\n' "Python executable value executed GNU Make syntax" >&2
  exit 1
fi

if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$MAKEFILE" MAKEFILE_LIST=/tmp/untrusted check) >"$TEMP_ROOT/command-list.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/command-list.out"
if (cd "$CONTROL_DIR" && MAKEFILE_LIST=/tmp/untrusted /usr/bin/make --environment-overrides --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/environment-list.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILE_LIST must not be overridden" "$TEMP_ROOT/environment-list.out"

PRELOADED="$TEMP_ROOT/preloaded.mk"
PRELOAD_MARKER="$TEMP_ROOT/preload-startup-ran"
printf '%s\n' "\$(shell /usr/bin/touch '$PRELOAD_MARKER')" >"$PRELOADED"
if (cd "$CONTROL_DIR" && MAKEFILES="$PRELOADED" /usr/bin/make --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/preloaded.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFILES must be empty" "$TEMP_ROOT/preloaded.out"
[ -e "$PRELOAD_MARKER" ]

EARLIER="$TEMP_ROOT/earlier.mk"
EARLIER_MARKER="$TEMP_ROOT/earlier-startup-ran"
printf '%s\n' "\$(shell /usr/bin/touch '$EARLIER_MARKER')" >"$EARLIER"
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$EARLIER" --file "$MAKEFILE" check) >"$TEMP_ROOT/earlier.out" 2>&1; then exit 1; fi
grep -Fq "repository Makefile path could not be resolved" "$TEMP_ROOT/earlier.out"
[ -e "$EARLIER_MARKER" ]

LATER="$TEMP_ROOT/later.mk"
LATER_MARKER="$TEMP_ROOT/later-startup-ran"
LATER_RECIPE_MARKER="$TEMP_ROOT/later-recipe-ran"
cat >"$LATER" <<EOF
\$(shell /usr/bin/touch '$LATER_MARKER')
lint:
	@/usr/bin/touch '$LATER_RECIPE_MARKER'
EOF
if (cd "$CONTROL_DIR" && SPLUNK_TORNADO_COMMAND_LOG="$COMMAND_LOG" /usr/bin/make --no-print-directory --file "$MAKEFILE" --file "$LATER" "PYTHON=$FAKE_PYTHON" lint) >"$TEMP_ROOT/later.out" 2>&1; then exit 1; fi
grep -Fq "repository Makefile must be loaded alone" "$TEMP_ROOT/later.out"
[ -e "$LATER_MARKER" ]
[ ! -e "$LATER_RECIPE_MARKER" ]

for flag in -n -t -q -i --just-print --touch --question --ignore-errors; do
  mode_name=$(printf '%s' "$flag" | /usr/bin/sed 's/^-*//; s/-/_/g')
  if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory "$flag" --file "$MAKEFILE" "PYTHON=$FAKE_PYTHON" lint) >"$TEMP_ROOT/mode-$mode_name.out" 2>&1; then exit 1; fi
  grep -Fq "non-executing or error-ignoring MAKEFLAGS are not supported" "$TEMP_ROOT/mode-$mode_name.out"
done
if (cd "$CONTROL_DIR" && MAKEFLAGS=-n /usr/bin/make --no-print-directory --file "$MAKEFILE" "PYTHON=$FAKE_PYTHON" lint) >"$TEMP_ROOT/environment-makeflags.out" 2>&1; then exit 1; fi
grep -Fq "non-executing or error-ignoring MAKEFLAGS are not supported" "$TEMP_ROOT/environment-makeflags.out"
if (cd "$CONTROL_DIR" && /usr/bin/make --no-print-directory --file "$MAKEFILE" MAKEFLAGS=-n "PYTHON=$FAKE_PYTHON" lint) >"$TEMP_ROOT/command-makeflags.out" 2>&1; then exit 1; fi
grep -Fq "MAKEFLAGS must not be overridden" "$TEMP_ROOT/command-makeflags.out"

printf '%s\n' "Makefile root tests passed: 35 executed target/authority cases, 1 dollar-syntax checkout case, 1 Python-value Make-syntax rejection, 2 MAKEFILE_LIST rejections, 3 contained startup-boundary cases, and 10 mode-flag rejections"
