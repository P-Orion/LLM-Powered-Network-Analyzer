import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

export interface AnalysisProgress {
  status: string;
  progress: number;
  message: string;
  results?: any;
}

@Injectable({
  providedIn: 'root'
})
export class AnalysisService {
  private ws: WebSocket | null = null;
  private progressSubject = new Subject<AnalysisProgress>();

  constructor() { }

  /**
   * Analyze a log file by sending it to the backend via WebSocket
   * @param fileContent The log file content as a string
   * @returns Observable that emits progress updates
   */
  analyzeFile(fileContent: string): Observable<AnalysisProgress> {
    // Close existing WebSocket if any
    if (this.ws) {
      this.ws.close();
    }

    // Create new WebSocket connection
    this.ws = new WebSocket('ws://localhost:8000/ws/analyze');

    // Handle WebSocket open
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      // Send file content to backend
      this.ws?.send(JSON.stringify({
        content: fileContent
      }));
    };

    // Handle incoming messages
    this.ws.onmessage = (event) => {
      const data: AnalysisProgress = JSON.parse(event.data);
      console.log('Received:', data);
      this.progressSubject.next(data);

      // Close WebSocket when analysis is complete or error occurs
      if (data.status === 'complete' || data.status === 'error') {
        this.ws?.close();
      }
    };

    // Handle WebSocket errors
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.progressSubject.next({
        status: 'error',
        progress: 0,
        message: 'Connection error. Please ensure the backend is running.'
      });
    };

    // Handle WebSocket close
    this.ws.onclose = () => {
      console.log('WebSocket closed');
    };

    return this.progressSubject.asObservable();
  }

  /**
   * Close the WebSocket connection
   */
  closeConnection(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
