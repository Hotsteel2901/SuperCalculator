$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..')
$Build = Join-Path $Root 'native/calc_core/build'

cmake -S (Join-Path $Root 'native/calc_core') -B $Build -DCMAKE_BUILD_TYPE=Release
cmake --build $Build --config Release
ctest --test-dir $Build -C Release --output-on-failure
Write-Host 'Native core build complete.'
