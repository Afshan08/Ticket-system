$files = Get-ChildItem -Path "c:\TicketSystem\frontend\forms\*.html"
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content

    # Fix the main tag class if it has static ml-64
    if ($content -match 'class="[^"]*ml-64 min-h-screen"') {
        $content = $content -replace 'class="[^"]*ml-64 min-h-screen"', 'class="p-8 transition-all duration-300 min-h-screen ml-0 md:ml-64"'
    }

    # Add mobile button if missing
    if (-not ($content -match 'id="mobile-menu-btn"')) {
        $btnHtml = '
        <div class="md:hidden mb-4">
             <button id="mobile-menu-btn" class="text-gray-600 hover:text-indigo-600 focus:outline-none">
                <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>
        </div>'
        # Insert after <main ...> tag
        # We look for the closing > of the main opening tag
        $content = $content -replace '(<main[^>]+>)', ('$1' + $btnHtml)
    }
    
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content
        Write-Host "Updated $($file.Name)"
    }
}

# Also handle index.html
$indexFile = "c:\TicketSystem\frontend\index.html"
if (Test-Path $indexFile) {
    $indexContent = Get-Content $indexFile -Raw
    $originalIndex = $indexContent
    
    if ($indexContent -match 'class="[^"]*ml-64 min-h-screen"') {
         $indexContent = $indexContent -replace 'class="[^"]*ml-64 min-h-screen"', 'class="p-8 transition-all duration-300 min-h-screen ml-0 md:ml-64"'
    }
    if (-not ($indexContent -match 'id="mobile-menu-btn"')) {
        $btnHtml = '
        <div class="md:hidden mb-4">
             <button id="mobile-menu-btn" class="text-gray-600 hover:text-indigo-600 focus:outline-none">
                <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>
        </div>'
        $indexContent = $indexContent -replace '(<main[^>]+>)', ('$1' + $btnHtml)
    }
    
    if ($indexContent -ne $originalIndex) {
        Set-Content -Path $indexFile -Value $indexContent
        Write-Host "Updated index.html"
    }
}
