import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';

import { UploadComponent } from './components/upload/upload.component';
import { ResultsComponent } from './components/results/results.component';
import { AnalysisService } from './services/analysis.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    CommonModule,
    MatToolbarModule,
    MatIconModule,
    UploadComponent,
    ResultsComponent
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'LLM Private Log Anomaly Finder';

  // Analysis state
  progress: number = 0;
  status: string = '';
  message: string = '';
  results: any = null;

  constructor(private analysisService: AnalysisService) {}

  /**
   * Handle file selection from upload component
   */
  onFileSelected(fileContent: string): void {
    // Reset state
    this.progress = 0;
    this.status = '';
    this.message = 'Starting analysis...';
    this.results = null;

    // Start analysis
    this.analysisService.analyzeFile(fileContent).subscribe({
      next: (update) => {
        this.progress = update.progress;
        this.status = update.status;
        this.message = update.message;

        if (update.status === 'complete' && update.results) {
          this.results = update.results;
        }
      },
      error: (error) => {
        console.error('Analysis error:', error);
        this.status = 'error';
        this.message = 'An unexpected error occurred during analysis.';
      }
    });
  }
}
