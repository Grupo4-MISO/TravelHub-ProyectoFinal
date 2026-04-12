Set-Location "d:/TRAVELHUB/BackEnd/TravelHub-ProyectoFinal"

$pairs = @(
    @('Baï¿½os','Baños'), @('Bastiï¿½n','Bastión'), @('Cabaï¿½a','Cabaña'), @('Cancï¿½n','Cancún'),
    @('Concepciï¿½n','Concepción'), @('Cï¿½rdoba','Córdoba'), @('Galï¿½pagos','Galápagos'), @('Habitaciï¿½n','Habitación'),
    @('Hospederï¿½a','Hospedería'), @('Mï¿½ncora','Máncora'), @('Montaï¿½ita','Montañita'), @('Mï¿½xico','México'),
    @('Perï¿½','Perú'), @('Tamacï¿½','Tamacá'), @('Valparaï¿½so','Valparaíso'), @('Viï¿½a','Viña'), @('Burï¿½','Buró'),
    @('Categorï¿½a','Categoría'), @('Chicï¿½','Chicó'), @('Clï¿½sica','Clásica'), @('Econï¿½mica','Económica'),
    @('Estï¿½ndar','Estándar'), @('Getsemanï¿½','Getsemaní'), @('Histï¿½rico','Histórico'), @('Isleï¿½o','Isleño'),
    @('Jardï¿½n','Jardín'), @('Marquï¿½s','Marqués'), @('Martï¿½n','Martín'), @('Mesï¿½n','Mesón'), @('Normandï¿½a','Normandía'),
    @('Panorï¿½mica','Panorámica'), @('Pequeï¿½a','Pequeña'), @('Pï¿½jaros','Pájaros'), @('vï¿½a','vía'), @('Volcï¿½n','Volcán')
)

Get-ChildItem "inventario_app/app/data/*_hospedajes_seed.json" | ForEach-Object {
    $txt = Get-Content $_.FullName -Raw
    foreach ($p in $pairs) {
        $txt = $txt.Replace($p[0], $p[1])
    }
    [System.IO.File]::WriteAllText($_.FullName, $txt, [System.Text.UTF8Encoding]::new($false))
}

Get-ChildItem "inventario_app/app/data/*_hospedajes_seed.json" | ForEach-Object {
    $arr = Get-Content $_.FullName -Raw | ConvertFrom-Json
    foreach ($item in $arr) {
        if ($item.PSObject.Properties.Name -contains 'Description') {
            $item.PSObject.Properties.Remove('Description')
        }
        if (-not ($item.PSObject.Properties.Name -contains 'description')) {
            $item | Add-Member -NotePropertyName description -NotePropertyValue ("Hospedaje en {0}, {1}." -f $item.ciudad, $item.pais) -Force
        }
    }
    $json = $arr | ConvertTo-Json -Depth 100
    [System.IO.File]::WriteAllText($_.FullName, $json, [System.Text.UTF8Encoding]::new($false))
}

Write-Output "ok"
