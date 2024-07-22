# BinDiversity-
To address these questions, this project makes several key contributions:

	1.	Identification of Significant Compiler Flags:
We systematically identify compiler flags that result in significantly different binary representations, providing insights into their impact on binary code. For example, optimization flags like -O1, -O2, and -O3 in GCC and Clang can produce binaries with varied performance and size characteristics, which are crucial for analysis. Therefore we use Bindiff to compare the produced binaries from different flags and get all the score from each function and aggregate the average and the standard deviation to analyze and identify the differences which has been produced by different flags.

	2.	Evaluation of Compiler Versions:
We assess the effects of different GCC and Clang versions on binary outputs with identical compiler flags, highlighting the variability introduced by compiler updates. Different versions of the same compiler can have subtle changes in code generation, impacting the final binary structure and behavior using Bindiff tool and aggregate the function similarity values to address the differences and evaluate this research question.

3.	Analysis of Binary Differences:
We investigate the correlation between bindiff equality and binary code identity, establishing the reliability of bindiff as a comparison tool. This helps in determining whether 100% equality in bindiff truly corresponds to 100% identical binary code. which has been evaluated by Bindiff therefore keep a closer look on the smiliraties Values to investigate how a similarity 1 (total similarty) using Ghidra Tool to the see and Alanyze the Binary codes to see how accurate is the total smiliraty by Bindiff .

4.Function Similarity Metrics: We identify functions with the highest dissimilarities and try to identify them for evaluating these dissimilarities, facilitating more effective binary analysis. Metrics such as the standard deviation of similarity scores help in understanding the consistency of function-level similarities across different binary versions. We address the functions with highest dissimilarities all over the Binary codes using standard deviation for the all the functions in the compiled package.

4.Diffing Tools : We continue the evaluation using additional binary diffing tools such as Diaphora. This involves compiling more packages like Binutils to create a diverse set of binary outputs for comparison. The focus is on comparing the tools and their characteristics.

