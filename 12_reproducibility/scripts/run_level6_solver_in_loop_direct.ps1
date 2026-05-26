$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$PythonExe = if ($env:PYTHON_EXE) { $env:PYTHON_EXE } else { "python" }
Set-Location -LiteralPath $Root

$LogDir = Join-Path $Root "10_results\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Out = Join-Path $LogDir "level6_solver_in_loop_direct.out.log"
$Err = Join-Path $LogDir "level6_solver_in_loop_direct.err.log"

try {
  "LEVEL6_SOLVER_PS_START $(Get-Date -Format o)" | Out-File -FilePath $Out -Encoding utf8
  "LEVEL6_SOLVER_PS_BEFORE_NATIVE $(Get-Date -Format o)" | Out-File -FilePath $Out -Encoding utf8 -Append

  & $PythonExe `
    "12_reproducibility\scripts\run_solver_in_loop_formal_main_suite.py" `
    --matrix-root "05_data_pipeline\processed\level4_formal_complex_j2_t6_8step_qp_9case" `
    --case-names "multi_hole_14x11,notch_14x11,curved_hole_14x11" `
    --models "hgo_qp_true_j2" `
    --train-load-paths "monotonic" `
    --eval-load-paths "monotonic,unload_reload,cyclic,nonproportional" `
    --seeds "20260517,20260518,20260519,20260520,20260521" `
    --epochs 50 `
    --batch-size 1 `
    --eval-batch-size 1 `
    --device "cuda" `
    --step-policy "all" `
    --no-skip-existing `
    --main-csv-out "11_paper\tables\solver_in_loop_formal_main_table.csv" `
    --main-md-out "11_paper\tables\solver_in_loop_formal_main_table.md" `
    --case-csv-out "11_paper\tables\solver_in_loop_formal_main_case_rows.csv" `
    --case-md-out "11_paper\tables\solver_in_loop_formal_main_case_rows.md" `
    --case-aggregate-csv-out "11_paper\tables\solver_in_loop_formal_main_case_aggregate.csv" `
    --case-aggregate-md-out "11_paper\tables\solver_in_loop_formal_main_case_aggregate.md" `
    --reduction-csv-out "11_paper\tables\solver_in_loop_formal_main_reduction.csv" `
    --reduction-md-out "11_paper\tables\solver_in_loop_formal_main_reduction.md" `
    --reduction-aggregate-csv-out "11_paper\tables\solver_in_loop_formal_main_reduction_aggregate.csv" `
    --reduction-aggregate-md-out "11_paper\tables\solver_in_loop_formal_main_reduction_aggregate.md" `
    >> $Out 2>> $Err

  $ExitCode = $LASTEXITCODE
  "LEVEL6_SOLVER_PS_AFTER_NATIVE $ExitCode $(Get-Date -Format o)" | Out-File -FilePath $Out -Encoding utf8 -Append
  "LEVEL6_SOLVER_PS_EXIT $ExitCode $(Get-Date -Format o)" | Out-File -FilePath $Out -Encoding utf8 -Append
  exit $ExitCode
} catch {
  "LEVEL6_SOLVER_PS_EXCEPTION $(Get-Date -Format o)" | Out-File -FilePath $Err -Encoding utf8 -Append
  $_ | Out-String | Out-File -FilePath $Err -Encoding utf8 -Append
  exit 1
}
