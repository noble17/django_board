#-*-coding:utf-8-*-

from django.shortcuts import render_to_response
from django.utils import timezone
from sample_board.models import DjangoBoard
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from sample_board.pagingHelper import pagingHelper

rowsPerPage = 2

def home(request):
	boardList = DjangoBoard.objects.order_by('-id')[0:2]
	current_page = 1
	
	totalCnt = DjangoBoard.objects.all().count()

	pagingHelperIns = pagingHelper();
        totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
        print 'totalPageList', totalPageList
        return render_to_response('listSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt, 'current_page':current_page, 'totalPageList':totalPageList} )

def show_write_form(request):
	return render_to_response('writeBoard.html')

@csrf_exempt
def DoWriteBoard(request):
	br = DjangoBoard(subject = request.POST['subject'], name = request.POST['name'], mail = request.POST['email'], memo = request.POST['memo'], created_date = timezone.now(), hits = 0 )

	br.save()
	
	url='/listSpecificPageWork?current_page=1'
	return HttpResponseRedirect(url)

def listSpecificPageWork(request):
	current_page = int(request.GET['current_page'])
	totalCnt = DjangoBoard.objects.all().count()
	print 'current_page=', current_page

	boardList = DjangoBoard.objects.raw('SELECT id, subject, name, created_date, mail, memo, hits FROM sample_board_djangoboard ORDER BY id DESC LIMIT %s, %s', [rowsPerPage*(current_page - 1), rowsPerPage])
    	print 'boardList=',boardList, 'count()=', totalCnt

	pagingHelperIns = pagingHelper();
    	totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)

	print 'totalPageList', totalPageList

    	return render_to_response('listSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt, 'current_page':current_page ,'totalPageList':totalPageList} )

def viewWork(request):
    	pk= request.GET['memo_id']
    	boardData = DjangoBoard.objects.get(id=pk)

    
    	# 조회수를 늘린다.    
    	DjangoBoard.objects.filter(id=pk).update(hits = boardData.hits + 1)

    
    	return render_to_response('viewMemo.html', {'memo_id': request.GET['memo_id'],
                                                'current_page':request.GET['current_page'],
                                                'searchStr': request.GET['searchStr'],
                                                'boardData': boardData } )

def listSearchedSpecificPageWork(request):
	searchStr = request.GET['searchStr']
	pageForView = int(request.GET['pageForView'])
	
	totalCnt = DjangoBoard.objects.filter(subject__contains=searchStr).count()

	pagingHelperlns = pagingHelper();
	totalPageList = pagingHelperlns.getTotalPageList(totalCnt, rowsPerPage)
	sumString = '%' + searchStr + '%'
	boardList = DjangoBoard.objects.raw("SELECT id, subject,name, created_date, mail, memo, hits FROM sample_board_djangoboard WHERE subject LIKE %s ORDER BY id DESC LIMIT %s,%s", [sumString, rowsPerPage*(pageForView-1), rowsPerPage])

	return render_to_response('listSearchedSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt, 'pageForView':pageForView ,'searchStr':searchStr, 'totalPageList':totalPageList} )

def listSpecificPageWork_to_update(request):
    	memo_id = request.GET['memo_id']
    	current_page = request.GET['current_page']
    	searchStr = request.GET['searchStr']
    	boardData = DjangoBoard.objects.get(id=memo_id)
    	return render_to_response('viewForUpdate.html', {'memo_id': request.GET['memo_id'],
                                                'current_page':request.GET['current_page'],
                                                'searchStr': request.GET['searchStr'],
                                                'boardData': boardData } )

@csrf_exempt
def updateBoard(request):
    	memo_id = request.POST['memo_id']
    	current_page = request.POST['current_page']
    	searchStr = request.POST['searchStr']

    	# Update DataBase
    	DjangoBoard.objects.filter(id=memo_id).update(
                                                  mail= request.POST['mail'],
                                                  subject= request.POST['subject'],
                                                  memo= request.POST['memo']
                                                  )

   	# Display Page => POST 요청은 redirection으로 처리하자
    	url = '/listSpecificPageWork?current_page=' + str(current_page)
    	return HttpResponseRedirect(url)

def DeleteSpecificRow(request):
	memo_id = request.GET['memo_id']
	current_page = request.GET['current_page']
	
	p = DjangoBoard.objects.get(id=memo_id)
	p.delete()

	totalCnt = DjangoBoard.objects.all().count()
	pagingHelperlns = pagingHelper();

	totalPageList = pagingHelperlns.getTotalPageList(totalCnt, rowsPerPage)
	print 'totalPages', totalPageList

	if( int(current_page) in totalPageList):
        	print 'current_page No Change'
        	current_page=current_page
    	
	else:
    	    current_page= int(current_page)-1
            print 'current_page--'

    	url = '/listSpecificPageWork?current_page=' + str(current_page)
    	return HttpResponseRedirect(url)

@csrf_exempt
def searchWithSubject(request):
	searchStr = request.POST['searchStr']
	print 'searchStr', searchStr

	url = '/listSearchedSpecificPageWork?searchStr='+searchStr+'&pageForView=1'
	return HttpResponseRedirect(url)
