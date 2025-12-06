import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './upload.component.html',
  styleUrl: './upload.component.scss'
})
export class UploadComponent {
  @Output() fileSelected = new EventEmitter<string>();

  selectedFile: File | null = null;
  isDragging = false;
  fileInfo: string = '';
  warningMessage: string = '';

  /**
   * Handle file selection via file input
   */
  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.processFile(file);
    }
  }

  /**
   * Handle drag over event
   */
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  /**
   * Handle drag leave event
   */
  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  /**
   * Handle file drop event
   */
  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.processFile(files[0]);
    }
  }

  /**
   * Process the selected file
   */
  processFile(file: File): void {
    this.selectedFile = file;

    // Validate file type - only pcapng files
    const validExtensions = ['.pcapng', '.pcap'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
      this.warningMessage = `Error: Only .pcapng and .pcap files are supported. Got: ${fileExtension}`;
      return; // Don't process invalid files
    } else {
      this.warningMessage = '';
    }

    // Calculate file size
    const fileSizeMB = file.size / (1024 * 1024);
    this.fileInfo = `${file.name} (${fileSizeMB.toFixed(2)} MB)`;

    // Show warning for large files
    if (fileSizeMB > 50 && fileSizeMB <= 200) {
      this.warningMessage = 'Large file detected. Analysis may take 2-5 minutes.';
    } else if (fileSizeMB > 200) {
      this.warningMessage = 'Very large file detected. Analysis may take 5-15 minutes. Consider filtering logs before upload.';
    }

    // Read file content as binary for pcapng files
    const reader = new FileReader();
    reader.onload = (e: any) => {
      // Convert to base64 for transmission to backend
      const arrayBuffer = e.target.result;
      const uint8Array = new Uint8Array(arrayBuffer);
      const binaryString = uint8Array.reduce((data, byte) => data + String.fromCharCode(byte), '');
      const base64Content = btoa(binaryString);
      this.fileSelected.emit(base64Content);
    };
    reader.readAsArrayBuffer(file);
  }

  /**
   * Trigger file input click
   */
  triggerFileInput(): void {
    const fileInput = document.getElementById('fileInput') as HTMLInputElement;
    fileInput?.click();
  }
}
