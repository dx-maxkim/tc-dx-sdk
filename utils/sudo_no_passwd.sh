#!/usr/bin/env bash
# sudo 그룹 사용자 전원에게 모든 명령어를 패스워드 없이 sudo 허용

set -euo pipefail

GROUP="sudo"
SUDO_FILE="/etc/sudoers.d/${GROUP}-nopasswd"

# 드롭인 파일 생성
TMP="$(mktemp)"
{
  echo "# Created $(date)"
  echo "%${GROUP} ALL=(ALL) NOPASSWD: ALL"
} > "$TMP"

# 문법 검증 후 배치
sudo visudo -cf "$TMP" >/dev/null
sudo install -m 0440 "$TMP" "$SUDO_FILE"
rm -f "$TMP"

echo "설정 완료: $SUDO_FILE"
echo "테스트: sudo -n true && echo OK || echo NG"

