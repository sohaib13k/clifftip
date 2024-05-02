function downloadExcel(jsonData) {
    if (!Array.isArray(jsonData)) {
        console.error('Data is not an array:', jsonData);
        return; // Exit if data is not an array
    }

    // Continue with Excel file creation if data is correct
    const worksheet = XLSX.utils.json_to_sheet(jsonData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Report");
    XLSX.writeFile(workbook, "Report.xlsx");
}
