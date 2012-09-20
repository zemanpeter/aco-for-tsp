all: doc_usr.pdf doc_prog.pdf

doc_usr.pdf: doc_usr.tex
	pdfcslatex doc_usr.tex

doc_prog.pdf: doc_prog.tex
	pdfcslatex doc_prog.tex

clean:
	rm *.aux *.log *.pdf
