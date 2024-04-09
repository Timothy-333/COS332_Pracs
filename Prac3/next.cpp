#include <iostream>
#include <fstream>
#include <cstdlib>

int main() 
{
    // Set HTTP headers to prevent caching
    std::cout << "Cache-Control: no-cache, no-store, must-revalidate\r\n";
    std::cout << "Pragma: no-cache\r\n";
    std::cout << "Expires: 0\r\n";
    
    // Set content type header
    std::cout << "Content-type:text/html\r\n\r\n";
    
    // Read Fibonacci sequence from file
    std::ifstream infile("fibonacci.txt");
    if (!infile) 
    {
        std::cerr << "Error: file could not be opened" << std::endl;
        return 1;
    }
    int x, y, z;
    infile >> x >> y >> z;
    infile.close();

    bool boundary = false;
    if (y == 0)
    {
        boundary = true;
    }
    // Calculate next Fibonacci number
    int new_num = y + z;
    // Update file with new sequence
    std::ofstream outfile("fibonacci.txt");
    if (!outfile) 
    {
        std::cerr << "Error: file could not be opened for writing" << std::endl;
        return 1;
    }
    outfile << y << " " << z << " " << new_num;
    outfile.close();

    std::cout << "<!DOCTYPE html>\n"
              << "<html>\n"
              << "<head>\n"
              << "<title>Fibonacci Sequence</title>\n"
              << "<style>\n"
              << "body {font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;}\n"
              << "p {font-size: 24px; color: #333;}\n"
              << "a {color: #0066cc; text-decoration: none; margin-right: 20px;}\n"
              << "</style>\n"
              << "</head>\n"
              << "<body>\n";
    std::cout << "<p>Fibonacci Sequence:</p>\n";
    std::cout << "<p>" << y << ", " << z << ", " << new_num << "</p>\n";
    if (!boundary)
        std::cout << "<a href=\"prev\">Previous</a>\n";
    std::cout << "<a href=\"next\">Next</a>\n";
    std::cout << "</body>\n"
              << "</html>\n";

    return 0;
}
