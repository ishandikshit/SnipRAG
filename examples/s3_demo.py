#!/usr/bin/env python
"""
Demo for SnipRAG showing how to process PDFs from S3 and search with image snippets.
"""

import os
import sys
import argparse
import base64
import io
from PIL import Image
import matplotlib.pyplot as plt

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sniprag import SnipRAGEngine

def display_results(results):
    """Display search results with image snippets."""
    # Set up matplotlib figure for displaying images
    n_results = len(results)
    if n_results == 0:
        print("No results found.")
        return
    
    fig, axes = plt.subplots(n_results, 1, figsize=(8, 4 * n_results))
    if n_results == 1:
        axes = [axes]  # Make it iterable when there's only one result
        
    # Display each result with its image snippet
    for i, result in enumerate(results):
        print(f"\n--- Match {i+1} (Page {result['metadata']['page_number']}) ---")
        print(f"Score: {result['score']:.4f}")
        
        # Truncate text if too long
        text = result['text']
        if len(text) > 300:
            text = text[:300] + "..."
        
        print(f"Text: {text}")
        
        # Display image snippet if available
        if "image_data" in result:
            try:
                # Decode the image
                image_data = base64.b64decode(result["image_data"])
                img = Image.open(io.BytesIO(image_data))
                
                # Display using matplotlib
                axes[i].imshow(img)
                axes[i].set_title(f"Match {i+1}: {text[:50]}...")
                axes[i].axis('off')
                
                print("Image snippet available - displaying with matplotlib")
            except Exception as e:
                print(f"Error displaying image: {str(e)}")
        else:
            print("No image snippet available")
            if "image_error" in result:
                print(f"Error: {result['image_error']}")
            
            # Display a placeholder
            axes[i].text(0.5, 0.5, "No image available", 
                      ha='center', va='center', transform=axes[i].transAxes)
            axes[i].axis('off')
    
    # Show the figure
    plt.tight_layout()
    plt.show()

def main():
    """Run the SnipRAG demo with S3 integration."""
    parser = argparse.ArgumentParser(description='SnipRAG S3 Demo')
    parser.add_argument('--s3-uri', type=str, help='S3 URI of the PDF (s3://bucket/path/to/file.pdf)')
    parser.add_argument('--aws-profile', type=str, help='AWS profile to use')
    parser.add_argument('--aws-region', type=str, default='us-east-1', help='AWS region')
    args = parser.parse_args()
    
    print("=== SnipRAG S3 Demo ===")
    print("This demo shows how to use SnipRAG with PDFs stored in S3.")
    
    # Get S3 URI from command line or user input
    s3_uri = args.s3_uri
    if not s3_uri:
        s3_uri = input("Enter S3 URI of the PDF (s3://bucket/path/to/file.pdf): ")
    
    if not s3_uri.startswith("s3://"):
        print("Error: Invalid S3 URI format. Must start with 's3://'.")
        return
    
    # Set up AWS credentials
    aws_credentials = {}
    
    # If a profile is specified, use boto3 Session to get credentials
    if args.aws_profile:
        import boto3
        from botocore.exceptions import ProfileNotFound
        
        try:
            # Create a session with the specified profile
            session = boto3.Session(profile_name=args.aws_profile)
            credentials = session.get_credentials()
            
            # Get credentials
            aws_credentials = {
                "aws_access_key_id": credentials.access_key,
                "aws_secret_access_key": credentials.secret_key,
                "region_name": args.aws_region
            }
            
            # Add session token if available
            if credentials.token:
                aws_credentials["aws_session_token"] = credentials.token
                
            print(f"Using AWS profile: {args.aws_profile}")
            
        except ProfileNotFound:
            print(f"Error: AWS profile '{args.aws_profile}' not found.")
            return
    else:
        # Use environment variables or instance profile if no profile specified
        print("Using default AWS credentials (from environment variables or instance profile)")
        aws_credentials = {"region_name": args.aws_region}
    
    # Initialize the SnipRAG engine with AWS credentials
    print("\nInitializing SnipRAG engine...")
    engine = SnipRAGEngine(aws_credentials=aws_credentials)
    
    # Process the PDF from S3
    print(f"Processing PDF from S3: {s3_uri}")
    document_id = s3_uri.split('/')[-1].replace('.pdf', '')  # Use filename without extension as document ID
    success = engine.process_document_from_s3(s3_uri, document_id)
    
    if not success:
        print("Error processing the PDF from S3. Exiting.")
        return
    
    print("PDF processed successfully!")
    
    # Interactive search loop
    while True:
        # Get search query
        print("\n" + "-" * 50)
        query = input("Enter search query (or 'quit' to exit): ")
        if query.lower() in ('quit', 'exit', 'q'):
            break
        
        # Get snippet padding
        try:
            padding = int(input("Enter padding for image snippets (default: 20): ") or "20")
        except ValueError:
            padding = 20
            print("Invalid input, using default padding of 20 pixels")
        
        # Filter for this document only
        filter_metadata = {"document_id": document_id}
        
        # Perform search with image snippets
        print(f"\nSearching for: '{query}'...")
        results = engine.search_with_snippets(
            query, 
            top_k=3, 
            filter_metadata=filter_metadata,
            snippet_padding=padding
        )
        
        # Display results
        display_results(results)
    
    print("\nThank you for using the SnipRAG S3 Demo!")

if __name__ == "__main__":
    main() 