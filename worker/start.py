# coding:utf8
from worker import commentpage_worker,download_img_worker,get_comments_photos_worker


if __name__ == '__main__':
    commentpage_worker=commentpage_worker.commentpage_worker()
    get_comments_photos_worker1=get_comments_photos_worker.get_comments_photos_worker()
    get_comments_photos_worker2=get_comments_photos_worker.get_comments_photos_worker()
    get_comments_photos_worker3=get_comments_photos_worker.get_comments_photos_worker()
    download_img_worker1=download_img_worker.download_img_worker()
    download_img_worker2=download_img_worker.download_img_worker()
    download_img_worker3=download_img_worker.download_img_worker()
    download_img_worker4=download_img_worker.download_img_worker()
    download_img_worker5=download_img_worker.download_img_worker()

    # 开工
    commentpage_worker.start()
    get_comments_photos_worker1.start()
    get_comments_photos_worker2.start()
    get_comments_photos_worker3.start()
    download_img_worker1.start()
    download_img_worker2.start()
    download_img_worker3.start()
    download_img_worker4.start()
    download_img_worker5.start()