#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["openpyxl>=3.1", "pillow"]
# ///
"""x1-extract.py 회귀 테스트. 픽스처를 openpyxl로 즉석 생성하므로 외부 파일이 없다.

usage: uv run test-x1-extract.py
- X1(.xlsx): 시트·표·셀·차트·이미지·병합 계수, 제목, 숨김 시트 제외, media 상대경로
- 값 정규화: 날짜 ISO, 정수형 float, 파이프 이스케이프, 줄바꿈 -> <br>
- 수식: 캐시 없는 수식은 원문 보존 + uncached 계수 + stderr 경고
- 절단: --max-rows/--max-cols 가 자르고 truncated=1 과 주석 마커를 남긴다
- 인자 파싱: 잘못된 플래그 형식·음수·미지원 확장자 거부
- .xls: LibreOffice가 있는 머신에서만 X2a 경로를 돈다 (없으면 skip)
"""
import datetime
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "x1-extract.py"
PY = sys.executable  # uv run 아래서는 openpyxl·pillow가 있는 인터프리터다

failures: list[str] = []


def check(cond: bool, label: str) -> None:
    print(("ok   " if cond else "FAIL ") + label)
    if not cond:
        failures.append(label)


def run_script(*args: str) -> tuple[int, str, str]:
    p = subprocess.run([PY, str(SCRIPT), *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def stats(stdout: str) -> dict[str, str]:
    lines = [l for l in stdout.splitlines() if l.startswith("stats ")]
    if not lines:
        sys.exit("no stats line in output — script probably failed; see FAIL lines above")
    # title= 은 마지막 키이고 공백을 포함할 수 있다 — 앞 11개 키만 공백으로 자른다
    return dict(kv.split("=", 1) for kv in lines[-1][len("stats "):].split(" ", 11))


def load_module():
    spec = importlib.util.spec_from_file_location("x1", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unit_tests() -> None:
    """순수 함수 검사 — 엑셀 없이 값 정규화 규칙만 본다."""
    x1 = load_module()
    check(x1.fmt_value(datetime.date(2026, 8, 3)) == "2026-08-03", "date -> ISO")
    check(x1.fmt_value(datetime.datetime(2026, 8, 3)) == "2026-08-03",
          "midnight datetime -> date only")
    check(x1.fmt_value(datetime.datetime(2026, 8, 3, 9, 30)) == "2026-08-03 09:30:00",
          "datetime with time -> ISO seconds")
    check(x1.fmt_value(4.0) == "4", "integral float -> int")
    check(x1.fmt_value(0.1 + 0.2) == "0.3", "float noise rounded")
    check(x1.fmt_value(True) == "TRUE" and x1.fmt_value(False) == "FALSE", "bool -> TRUE/FALSE")
    check(x1.fmt_value(None) == "", "None -> empty")
    check(x1.escape_cell("a|b") == "a\\|b", "pipe escaped")
    check(x1.escape_cell("a\nb") == "a<br>b", "newline -> <br>")
    check(x1.escape_cell("a\x00b") == "ab", "control chars stripped")
    check(x1.formula_text("=SUM(A1:A2)") == "=SUM(A1:A2)", "formula detected")
    check(x1.formula_text("not a formula") is None, "plain string is not a formula")
    check(x1.column_letter(1) == "A" and x1.column_letter(27) == "AA", "column letters")
    check(x1.leaked_absolute("![x](/tmp/a.png)"), "detects posix absolute link")
    check(x1.leaked_absolute("![x](C:\\tmp\\a.png)"), "detects Windows absolute link")
    check(not x1.leaked_absolute("![x](media/a.png)"), "relative media link is not a leak")


def build_fixture(path: Path, png: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.chart import BarChart, Reference
    from openpyxl.drawing.image import Image as XLImage
    from PIL import Image as PILImage

    wb = Workbook()
    ws = wb.active
    ws.title = "점검 기준"
    for row in [
        ["설비코드", "점검 항목", "기준 온도(℃)", "허용 오차(±)", "점검일", "합격"],
        ["EQ-101", "냉각수 순환", 23.5, 1.5, datetime.date(2026, 8, 3), True],
        ["EQ-102", "압력 밸브 | 2차", 4.0, 0.25, datetime.date(2026, 8, 4), False],
        ["EQ-103", "여과기\n교체 주기", 0.1 + 0.2, 0.05, datetime.datetime(2026, 8, 5, 9, 30), True],
    ]:
        ws.append(row)
    ws["A6"] = "평균"
    ws["C6"] = "=AVERAGE(C2:C4)"  # openpyxl이 만든 파일이라 계산 캐시가 없다
    ws.merge_cells("A8:C8")
    ws["A8"] = "비고: 병합 셀 테스트"

    ws2 = wb.create_sheet("요금표")
    ws2.append(["구간", "단가"])
    for i in range(1, 260):
        ws2.append([f"구간-{i}", i * 100])
    chart = BarChart()
    chart.add_data(Reference(ws2, min_col=2, min_row=1, max_row=10))
    ws2.add_chart(chart, "D2")

    ws3 = wb.create_sheet("숨김메모")
    ws3["A1"] = "내부 스크래치"
    ws3.sheet_state = "hidden"

    ws4 = wb.create_sheet("로고")
    PILImage.new("RGB", (24, 24), (200, 40, 40)).save(png)
    ws4["A1"] = "표지"
    ws4.add_image(XLImage(str(png)), "B2")

    wb.properties.title = "설비 점검 기준표"
    wb.save(path)


def main() -> None:
    unit_tests()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        xlsx = work / "fixture.xlsx"
        build_fixture(xlsx, work / "logo.png")

        # ── X1 ──────────────────────────────────────────
        out = work / "x1.md"
        media = work / "m1"
        rc, so, se = run_script(str(xlsx), str(out), f"--media-dir={media}")
        check(rc == 0, "X1 exits 0")
        s = stats(so)
        check(s["path"] == "X1", f"X1 path (got {s['path']})")
        check(s["sheets"] == "3", f"X1 renders 3 visible sheets (got {s['sheets']})")
        check(s["hidden"] == "1", f"X1 skips 1 hidden sheet (got {s['hidden']})")
        check(s["charts"] == "1", f"X1 charts=1 (got {s['charts']})")
        check(s["images"] == "1", f"X1 images=1 (got {s['images']})")
        check(s["merges"] == "1", f"X1 merges=1 (got {s['merges']})")
        check(s["uncached"] == "1", f"X1 uncached=1 (got {s['uncached']})")
        check(s["truncated"] == "1", "X1 truncated=1 (260-row sheet over the 200 default)")
        check(s["title"] == "설비 점검 기준표", f"X1 title (got {s['title']})")
        check("warning:" in se and "수식" in se, "uncached formula warned on stderr")

        md = out.read_text(encoding="utf-8")
        check("## 점검 기준" in md and "## 요금표" in md, "sheet names become H2")
        check("## 숨김메모" not in md, "hidden sheet excluded")
        check("=AVERAGE(C2:C4)" in md, "uncached formula text preserved, not blanked")
        check("압력 밸브 \\| 2차" in md, "pipe escaped in cell")
        check("여과기<br>교체 주기" in md, "newline became <br>")
        check("2026-08-03" in md and "2026-08-05 09:30:00" in md, "dates as ISO")
        check("| 0.3 |" in md, "float noise normalized in output")
        check("℃" in md and "±" in md and "EQ-101" in md, "units and codes intact")
        check("<!-- truncated:" in md, "truncation marker emitted")
        check("병합 셀 1개" in md, "merge note emitted")
        check("차트 1개" in md, "chart note emitted")
        check("media/" in md and str(media) not in md, "media path relative, no absolute leak")
        check(any((media / "media").glob("*")), "image extracted under DIR/media/")
        check(len([l for l in md.splitlines() if l.strip() == "|  |  |  |  |  |  |"]) == 0,
              "spacer rows dropped")

        # ── 절단 경계 ──────────────────────────────────
        out2 = work / "x1-small.md"
        rc, so, _ = run_script(str(xlsx), str(out2), "--max-rows=3", "--max-cols=2")
        check(rc == 0, "X1 with limits exits 0")
        md2 = out2.read_text(encoding="utf-8")
        check("cols 3-6 of 6" in md2, "column truncation reported")
        check("기준 온도(℃)" not in md2, "columns past --max-cols dropped")
        check(stats(so)["truncated"] == "1", "limits set truncated=1")

        # ── 인자·확장자 거부 ────────────────────────────
        rc, _, se = run_script(str(xlsx), str(work / "x.md"), "--max-rows", "5")
        check(rc != 0, "space-separated --max-rows rejected")
        rc, _, se = run_script(str(xlsx), str(work / "x.md"), "--max-rows=0")
        check(rc != 0 and "positive integer" in se, "--max-rows=0 rejected")
        rc, _, se = run_script(str(xlsx), str(work / "x.md"), "--bogus=1")
        check(rc != 0 and "unknown flag" in se, "unknown flag rejected")
        csv = work / "data.csv"
        csv.write_text("a,b\n1,2\n", encoding="utf-8")
        rc, _, se = run_script(str(csv), str(work / "x.md"))
        check(rc != 0 and "unsupported extension" in se, "csv rejected with a reason")

        # ── X2a (.xls — LibreOffice 있을 때만) ───────────
        x1 = load_module()
        if x1.find_soffice():
            legacy = work / "legacy.xls"
            subprocess.run(
                [x1.find_soffice(), f"-env:UserInstallation={(work / 'p').as_uri()}",
                 "--headless", "--convert-to", "xls", "--outdir", str(work), str(xlsx)],
                capture_output=True, check=True,
            )
            if legacy.exists():
                out3 = work / "x2.md"
                rc, so, _ = run_script(str(legacy), str(out3))
                check(rc == 0, "X2a exits 0")
                s3 = stats(so)
                check(s3["path"] == "X2a", f"X2a path (got {s3['path']})")
                check("EQ-101" in out3.read_text(encoding="utf-8"), "X2a content intact")
            else:
                print("skip X2a (soffice produced no .xls)")
        else:
            print("skip X2a (no LibreOffice)")

    print()
    if failures:
        sys.exit(f"{len(failures)} failure(s): " + "; ".join(failures))
    print("all passed")


if __name__ == "__main__":
    main()
